"""Case-level warmup + fine-tuning; validation selection, no test access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
import yaml
from .model import CaseGradabilityModel,ARCHITECTURE
from .preprocessing import load_image,model_transform,MEAN,STD
from .evaluate import binary_metrics


class CaseDataset(Dataset):
    def __init__(self,records,raw_dir,training=False):
        self.records=records;self.raw_dir=Path(raw_dir);self.transform=model_transform(training)
    def __len__(self):return len(self.records)
    def __getitem__(self,index):
        row=self.records[index]
        images=[self.transform(load_image(self.raw_dir/'images'/Path(p).name)[0]) for p in row['image_paths']]
        return images,row['label'],row['case_id']


def collate_cases(batch):
    tensors=[];indices=[];labels=[];ids=[]
    for index,(images,label,case_id) in enumerate(batch):
        tensors.extend(images);indices.extend([index]*len(images));labels.append(label);ids.append(case_id)
    return torch.stack(tensors),torch.tensor(indices),torch.tensor(labels),ids


def validation(model,loader,device):
    model.eval();labels=[];scores=[];ids=[];losses=[]
    with torch.inference_mode():
        for images,indices,y,case_ids in loader:
            logits=model(images.to(device),indices.to(device),len(y))
            losses.append(float(nn.functional.cross_entropy(logits,y.to(device)).item())*len(y))
            labels.extend(y.tolist());scores.extend(logits.softmax(1)[:,1].cpu().tolist());ids.extend(case_ids)
    return ids,labels,scores,sum(losses)/len(labels)


def train(config_path='configs/experiment.yaml',processed_dir=None,raw_dir=None,checkpoint_dir=None,report_dir=None,epochs=None):
    config=yaml.safe_load(Path(config_path).read_text());seed=config['seed']
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    torch.set_num_threads(2);torch.backends.nnpack.set_flags(False)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    processed_dir=Path(processed_dir or config['data']['processed_dir']);raw_dir=Path(raw_dir or config['data']['raw_dir'])
    checkpoint_dir=Path(checkpoint_dir or config['training']['checkpoint_dir']);report_dir=Path(report_dir or config.get('reports_dir','reports'))
    records=[json.loads(line) for line in (processed_dir/'cases.jsonl').read_text().splitlines()]
    training=[r for r in records if r['split']=='train'];val=[r for r in records if r['split']=='validation']
    if not training or not val:raise ValueError('Prepared train and validation cases required')
    count_epochs=epochs or config['training']['epochs']
    if count_epochs<2:raise ValueError('At least two epochs needed for warmup and actual fine-tuning')
    generator=torch.Generator().manual_seed(seed)
    batch_size=config['training']['batch_size']
    train_loader=DataLoader(CaseDataset(training,raw_dir,True),batch_size=batch_size,shuffle=True,generator=generator,collate_fn=collate_cases)
    val_loader=DataLoader(CaseDataset(val,raw_dir),batch_size=batch_size,collate_fn=collate_cases)
    model=CaseGradabilityModel(pretrained=True).to(device)
    counts=np.bincount([r['label'] for r in training],minlength=2)
    weights=torch.tensor(len(training)/(2*counts),dtype=torch.float32,device=device)
    criterion=nn.CrossEntropyLoss(weight=weights)
    for parameter in model.backbone.parameters():parameter.requires_grad=False
    optimizer=torch.optim.AdamW(model.classifier.parameters(),lr=config['training']['learning_rate'],weight_decay=.0001)
    checkpoint_dir.mkdir(parents=True,exist_ok=True);report_dir.mkdir(parents=True,exist_ok=True)
    history=[];best_key=(-1,-1);start=time.time();best=None
    for epoch in range(1,count_epochs+1):
        if epoch==2:
            for parameter in model.backbone.parameters():parameter.requires_grad=True
            optimizer=torch.optim.AdamW(model.parameters(),lr=config['training'].get('finetune_learning_rate',.0001),weight_decay=.0001)
        model.train()
        if epoch==1:model.backbone.eval()
        # Keep pretrained BN statistics stable with small, variable-size case batches.
        for module in model.backbone.modules():
            if isinstance(module,nn.modules.batchnorm._BatchNorm):module.eval()
        running=0
        for images,indices,y,_ in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits=model(images.to(device),indices.to(device),len(y))
            loss=criterion(logits,y.to(device));loss.backward();optimizer.step()
            running+=float(loss.item())*len(y)
        ids,labels,scores,val_loss=validation(model,val_loader,device)
        metrics=binary_metrics(labels,scores)
        row={'epoch':epoch,'phase':'head_warmup' if epoch==1 else 'backbone_finetuning',
             'train_weighted_loss':running/len(training),'validation_loss':val_loss,**metrics}
        history.append(row)
        key=(metrics['balanced_accuracy'],metrics['roc_auc_gradable'])
        if key>best_key:
            best_key=key;best=row
            checkpoint={'state_dict':{k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                        'architecture':ARCHITECTURE,'epoch':epoch,'seed':seed,'class_order':['ungradable','gradable'],
                        'preprocessing':{'image_size':224,'letterbox':True,'mean':list(MEAN),'std':list(STD)},
                        'training_config':config,'validation_metrics':metrics,'case_aggregation':'mean_embeddings',
                        'initialization':'ImageNet pretrained timm weights','research_only':True}
            temporary=checkpoint_dir/'best.pt.tmp';torch.save(checkpoint,temporary);temporary.replace(checkpoint_dir/'best.pt')
            (processed_dir/'cnn_validation_predictions.json').write_text(json.dumps({'case_ids':ids,'labels':labels,'scores':scores},indent=2)+'\n')
        print(json.dumps({'epoch':epoch,'phase':row['phase'],'balanced_accuracy':metrics['balanced_accuracy'],'roc_auc':metrics['roc_auc_gradable'],'elapsed_seconds':round(time.time()-start)}),flush=True)
    report={'split':'validation','test_evaluated':False,'device':str(device),'epochs_completed':count_epochs,
            'selected_epoch':best['epoch'],'selection_metric':'validation balanced accuracy; ROC-AUC tie-break',
            'train_cases':len(training),'validation_cases':len(val),'history':history,'best':best,
            'checkpoint_sha256':hashlib.sha256((checkpoint_dir/'best.pt').read_bytes()).hexdigest(),
            'elapsed_seconds':round(time.time()-start,2),'single_image_limit':'Case model uses fewer inputs for a single-image upload; clinical adequacy is not validated'}
    (report_dir/'training_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/experiment.yaml')
    for name in ['processed-dir','raw-dir','checkpoint-dir','report-dir']:p.add_argument('--'+name)
    p.add_argument('--epochs',type=int);a=p.parse_args()
    train(a.config,a.processed_dir,a.raw_dir,a.checkpoint_dir,a.report_dir,a.epochs)
