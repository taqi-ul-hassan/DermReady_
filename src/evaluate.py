"""Binary and three-state metrics with explicit denominators; no automatic test access."""
import numpy as np
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, roc_auc_score, average_precision_score


def binary_metrics(labels, scores, threshold=.5):
    raw=np.asarray(labels);p=np.asarray(scores,dtype=float)
    if raw.ndim!=1 or p.ndim!=1 or not len(raw) or len(raw)!=len(p) or not np.isin(raw,[0,1]).all() or not np.isfinite(p).all() or ((p<0)|(p>1)).any() or not np.isfinite(threshold) or not 0<=threshold<=1:
        raise ValueError('Matching nonempty binary labels and finite scores/threshold in [0,1] required')
    y=raw.astype(int);pred=(p>=threshold).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'unit':'case','threshold':float(threshold),'cases':len(y),
            'class_counts':{'ungradable':int((y==0).sum()),'gradable':int((y==1).sum())},
            'ungradable_recall':float(tn/(tn+fp)) if tn+fp else None,
            'false_acceptance_rate':float(fp/(tn+fp)) if tn+fp else None,
            'gradable_acceptance_rate':float(tp/(tp+fn)) if tp+fn else None,
            'false_rejection_rate':float(fn/(tp+fn)) if tp+fn else None,
            'f1_ungradable':float(f1_score(y,pred,pos_label=0,zero_division=0)),
            'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
            'roc_auc_gradable':float(roc_auc_score(y,p)) if len(set(y))==2 else None,
            'pr_auc_ungradable':float(average_precision_score(1-y,1-p)),
            'confusion_matrix_rows_actual_0_1_cols_predicted_0_1':[[int(tn),int(fp)],[int(fn),int(tp)]]}


def wilson_interval(successes,total):
    if total==0:return None
    p=successes/total;z=1.959963984540054
    denominator=1+z*z/total
    center=(p+z*z/(2*total))/denominator
    margin=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/denominator
    return [float(max(0,center-margin)),float(min(1,center+margin))]


def three_state_metrics(labels, states):
    """Case-label weak proxy; uncertain cases remain in error-rate denominators."""
    from .feedback import RETAKE, UNCERTAIN, SUITABLE
    raw=np.asarray(labels);s=np.asarray(states)
    ordered=[RETAKE,UNCERTAIN,SUITABLE]
    if raw.ndim!=1 or s.ndim!=1 or len(raw)!=len(s) or not len(raw) or not np.isin(raw,[0,1]).all() or not set(s).issubset(set(ordered)):
        raise ValueError('Nonempty matching labels and supported states required')
    y=raw.astype(int)
    n0=int((y==0).sum());n1=int((y==1).sum())
    fa=int(((y==0)&(s==SUITABLE)).sum());fr=int(((y==1)&(s==RETAKE)).sum())
    ungradable_retake=int(((y==0)&(s==RETAKE)).sum())
    counts={state:int((s==state).sum()) for state in ordered}
    return {'cases':len(y),'class_counts':{'ungradable':n0,'gradable':n1},'state_counts':counts,
            'matrix_rows_actual_0_1_cols_retake_uncertain_suitable':[[int(((y==label)&(s==state)).sum()) for state in ordered] for label in [0,1]],
            'false_acceptance_count':fa,'false_acceptance_rate_all_ungradable':fa/n0 if n0 else None,
            'false_acceptance_wilson95':wilson_interval(fa,n0),
            'false_rejection_count':fr,'false_rejection_rate_all_gradable':fr/n1 if n1 else None,
            'false_rejection_wilson95':wilson_interval(fr,n1),
            'ungradable_retake_recall':ungradable_retake/n0 if n0 else None,
            'uncertainty_fraction':counts[UNCERTAIN]/len(y),
            'decision_coverage':(counts[RETAKE]+counts[SUITABLE])/len(y),
            'accepted_ungradable_fraction':fa/counts[SUITABLE] if counts[SUITABLE] else None,
            'denominators':'False acceptance and retake recall: all ungradable cases. False rejection: all gradable cases. Coverage: all cases. Accepted contamination: all suitable outputs. Uncertain outputs remain in total/class denominators.',
            'interpretation':'Three-state recall counts explicit retake only; uncertainty is not a correct rejection. Binary F1/balanced accuracy are reported separately at fixed 0.5.'}

