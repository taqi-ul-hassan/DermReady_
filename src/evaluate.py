"""Binary and three-state metrics with explicit denominators; no automatic test access."""
import numpy as np
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, roc_auc_score, average_precision_score


def binary_metrics(labels, scores, threshold=.5):
    y=np.asarray(labels,dtype=int);p=np.asarray(scores,dtype=float);pred=(p>=threshold).astype(int)
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
