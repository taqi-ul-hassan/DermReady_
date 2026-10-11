"""Load artifacts once; keep image processing and prediction independent of UI."""
import json
from pathlib import Path
import numpy as np
import torch
from .model import CaseGradabilityModel,ARCHITECTURE
from .artifact_validation import validate_policy,validate_baseline,validate_thresholds
from .preprocessing import load_image,preprocess_for_inference
from .quality_features import extract_quality_features,aggregate_quality_features
from .feedback import decide_with_reason,make_feedback,quality_flags,UNCERTAIN


class Predictor:
    def __init__(self,checkpoint_dir='checkpoints',report_dir='reports',model_name=None):
        self.directory=Path(checkpoint_dir);self.model=None;self.baseline=None
        policy_path=self.directory/'decision_policy.json'
        report_dir=Path(report_dir)
        self.load_warnings=[]
        self.policy=None
        if policy_path.exists():
            try:self.policy=validate_policy(json.loads(policy_path.read_text()))
            except (OSError,ValueError,KeyError,TypeError):
                self.load_warnings.append('Decision policy is invalid or unreadable; showing capture indicators only.')
        self.quality_thresholds=self.policy['quality_thresholds'] if self.policy else None
        qpath=report_dir/'quality_thresholds.json'
        if self.quality_thresholds is None and qpath.exists():
            try:self.quality_thresholds=validate_thresholds(json.loads(qpath.read_text()))
            except (OSError,ValueError,KeyError,TypeError):pass
        if (self.directory/'best.pt').exists() and self.policy and 'cnn' in self.policy['models']:
            try:
                checkpoint=torch.load(self.directory/'best.pt',map_location='cpu',weights_only=True)
                if checkpoint['architecture']!=ARCHITECTURE or checkpoint['class_order']!=['ungradable','gradable']:
                    raise ValueError('Model artifact does not match architecture/class order.')
                self.model=CaseGradabilityModel(pretrained=False).eval();self.model.load_state_dict(checkpoint['state_dict'])
            except Exception:
                self.model=None;self.load_warnings.append('CNN artifact unavailable; using a supported fallback.')
        if (self.directory/'quality_baseline.json').exists() and self.policy and 'quality_baseline' in self.policy['models']:
            try:self.baseline=validate_baseline(json.loads((self.directory/'quality_baseline.json').read_text()))
            except (OSError,ValueError,KeyError,TypeError):
                self.load_warnings.append('Feature baseline is invalid or unreadable; using an available supported system.')
        preferred=model_name or (self.policy['preferred_model'] if self.policy else None)
        available={'cnn':self.model is not None,'quality_baseline':self.baseline is not None}
        if model_name and not available.get(model_name):raise ValueError('Requested model artifact is unavailable.')
        self.mode=preferred if available.get(preferred) else next((name for name,ready in available.items() if ready),'features_only')
        torch.set_num_threads(2);torch.backends.nnpack.set_flags(False)

    def predict(self,source):
        image,metadata=load_image(source);features=extract_quality_features(image)
        score=None
        if self.mode=='cnn':
            with torch.inference_mode():score=float(self.model(preprocess_for_inference(image).unsqueeze(0)).softmax(1)[0,1])
        elif self.mode=='quality_baseline':
            case_features=aggregate_quality_features([features]);b=self.baseline
            x=np.array([case_features[name] for name in b['columns']],dtype=float)
            z=float(((x-np.array(b['mean']))/np.array(b['scale']))@np.array(b['coefficient'])+b['intercept'])
            score=float(1/(1+np.exp(-np.clip(z,-40,40))))
        if score is not None and self.policy and self.quality_thresholds:
            state,flags,reason=decide_with_reason(score,self.policy['models'][self.mode],features,metadata,self.quality_thresholds)
        else:
            state=UNCERTAIN
            flags=quality_flags(features,self.quality_thresholds) if self.quality_thresholds else []
            reason='Fitted model artifacts or a valid decision policy are unavailable; showing capture indicators only.'
        feedback=make_feedback(state,flags)
        if self.load_warnings:feedback=' '.join(self.load_warnings)+'\n\n'+feedback
        if self.mode=='features_only':feedback='Model artifacts are unavailable. Showing capture indicators only; no learned suitability decision.\n\n'+feedback
        return {'state':state,'score':score,'model':self.mode,'features':features,'metadata':metadata,
                'flags':flags,'feedback':feedback,'decision_reason':reason,'preview':image}
