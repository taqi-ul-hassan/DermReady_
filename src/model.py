"""Pretrained image encoder with mean embedding aggregation and two case logits."""
import timm
import torch
from torch import nn

ARCHITECTURE = 'mobilenetv3_small_100.lamb_in1k'


class CaseGradabilityModel(nn.Module):
    def __init__(self, pretrained=False):
        super().__init__()
        self.backbone=timm.create_model(ARCHITECTURE,pretrained=pretrained,num_classes=0)
        self.classifier=nn.Linear(self.backbone.head_hidden_size,2)

    def forward(self,images,case_indices=None,case_count=None):
        embeddings=self.backbone(images)
        if case_indices is None:
            pooled=embeddings
        else:
            if case_count is None:case_count=int(case_indices.max().item())+1
            pooled=embeddings.new_zeros((case_count,embeddings.shape[1])).index_add(0,case_indices,embeddings)
            counts=torch.bincount(case_indices,minlength=case_count).clamp_min(1).to(embeddings.dtype)
            pooled=pooled/counts[:,None]
        return self.classifier(pooled)
