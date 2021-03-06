# -*- coding: utf-8 -*-
"""klf_training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O4EYuyjQPdHRtwG2azKTUB7g0IqPnSfT
"""

from google.colab import drive
drive.mount('/content/gdrive')

import os
import pandas as pd
import numpy as np
data_dir = 'gdrive/My Drive/protein/klf' # For Google CoLab

# df_aac = pd.read_csv(os.path.join(data_dir,'pseaac','AAC.csv'))
# df_dc = pd.read_csv(os.path.join(data_dir,'pseaac','DC.csv'))
# df_tc = pd.read_csv(os.path.join(data_dir,'pseaac','TC.csv'))
df_paac = pd.read_csv(os.path.join(data_dir,'ifeature','refseq_paac.cv.csv'))
df_apaac = pd.read_csv(os.path.join(data_dir,'ifeature','refseq_apaac.cv.csv'))
df_qso = pd.read_csv(os.path.join(data_dir,'ifeature','refseq_qso.cv.csv'))
df_cksaap = pd.read_csv(os.path.join(data_dir,'ifeature','refseq_cksaap.cv.csv'))
df_cksaagp = pd.read_csv(os.path.join(data_dir,'ifeature','refseq_cksaagp.cv.csv'))

# X_trn_aac = df_aac.drop('Label', axis=1)
# X_trn_dc = df_dc.drop('Label', axis=1)
# X_trn_tc = df_tc.drop('Label', axis=1)
X_trn_apaac = df_apaac.drop('Label', axis=1)
X_trn_cksaagp = df_cksaagp.drop('Label', axis=1)
X_trn_cksaap = df_cksaap.drop('Label', axis=1)
X_trn_paac = df_paac.drop('Label', axis=1)
X_trn_qso = df_qso.drop('Label', axis=1)
y_trn = df_paac['Label']

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
from collections import Counter
from sklearn import metrics
from xgboost import XGBClassifier

def libsvm_model():
    clf = SVC(C=8, gamma=8, kernel='rbf', probability=True)
    return clf

def libsvm_model_weight():
    clf = SVC(C=8, gamma=8, kernel='rbf', probability=True, class_weight='balanced')
    return clf

def mlp_model():
    mlp = MLPClassifier()
    return mlp

def knn_model():
    knn = KNeighborsClassifier(n_neighbors=10)
    return knn

def randomforest_model():
    rf = RandomForestClassifier(random_state = 42, max_features='auto', n_estimators=200, criterion='entropy', max_depth=7)
    return rf

def xgb_model():
    xgb = XGBClassifier(subsample=0.6, min_child_weight=1, max_depth=5, gamma=1.5, colsample_bytree=0.8)
    return xgb

"""### Plot ROC Curves for features"""

def calculate_ROC(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
     
    # Train SVM classifier
    model = xgb_model()
    model.fit(X_train, y_train)

    # Probability
    pred_prob = model.predict_proba(X_test)

    #GET ROC DATA
    fpr, tpr, thresholds = roc_curve(y_test, pred_prob[:,1], pos_label=1)
    roc_auc = auc(fpr, tpr)
    
    return fpr, tpr, roc_auc

def calculate_PRC(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
     
    # Train SVM classifier
    model = randomforest_model()
    model.fit(X_train, y_train)

    # Probability
    pred_prob = model.predict_proba(X_test)
    
    # predict class values
    yhat = model.predict(X_test)

    #GET ROC DATA
    precision, recall, _ = precision_recall_curve(y_test, pred_prob[:,1])
    f1, prc_auc = f1_score(y_test, yhat), auc(recall, precision)
    
    return recall, precision, f1

import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split

fpr_apaac, tpr_apaac, roc_auc_apaac = calculate_ROC(X_trn_apaac, y_trn)
fpr_cksaagp, tpr_cksaagp, roc_auc_cksaagp = calculate_ROC(X_trn_cksaagp, y_trn)
fpr_cksaap, tpr_cksaap, roc_auc_cksaap = calculate_ROC(X_trn_cksaap, y_trn)
fpr_paac, tpr_paac, roc_auc_paac = calculate_ROC(X_trn_paac, y_trn)
fpr_qso, tpr_qso, roc_auc_qso = calculate_ROC(X_trn_qso, y_trn)

# Plot ROC Curve
fig = plt.figure(figsize=(15,15))
plt.xlabel('False Positive Rate', fontsize=20)
plt.ylabel('True Positive Rate', fontsize=20)
plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
#plt.title('SVM Classifier ROC', fontsize=20)
plt.plot(fpr_apaac, tpr_apaac, marker='.',lw=4, label='APAAC (AUC = %0.3f)' % roc_auc_apaac)
plt.plot(fpr_cksaagp, tpr_cksaagp, marker=',', ls='-',lw=4, label='CKSAAGP (AUC = %0.3f)' % roc_auc_cksaagp)
plt.plot(fpr_cksaap, tpr_cksaap, marker='o', ls='-',lw=4, label='CKSAAP (AUC = %0.3f)' % roc_auc_cksaap)
plt.plot(fpr_paac, tpr_paac, marker='v', ls='-',lw=4, label='PAAC (AUC = %0.3f)' % roc_auc_paac)
plt.plot(fpr_qso, tpr_qso, marker='^', ls='-',lw=4, label='QSO (AUC = %0.3f)' % roc_auc_qso)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(loc="lower right", prop={'size': 20})
plt.show()

fig.savefig(os.path.join(data_dir, 'figures', 'feat.xgb.cv.roc.png'), dpi=300, bbox_inches='tight')

"""### Hybrid features"""

X_trn_hybrid = pd.concat([X_trn_cksaap, X_trn_cksaagp, X_trn_qso, X_trn_apaac, X_trn_paac], axis=1)

from sklearn.feature_selection import RFECV

clf = xgb_model()
# classifications
rfecv = RFECV(estimator=clf, step=1, cv=StratifiedKFold(5),
              scoring='accuracy')
rfecv.fit(X_trn_hybrid, y_trn)

print("Optimal number of features : %d" % rfecv.n_features_)

# Plot number of features VS. cross-validation scores
plt.figure()
plt.xlabel("Number of features selected")
plt.ylabel("Cross validation score (nb of correct classifications)")
plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
plt.show()

"""### Model Training"""

kfold = StratifiedKFold(n_splits=5, shuffle=True)

for train, test in kfold.split(X_trn_cksaap, y_trn):
#    train_x, train_y = X_trn.iloc[train], Y_trn.iloc[train]
    svm_model = libsvm_model_weight()   
    ## evaluate the model
    svm_model.fit(X_trn_cksaap.iloc[train], y_trn.iloc[train])
    # evaluate the model
    true_labels = np.asarray(y_trn.iloc[test])
    predictions = svm_model.predict(X_trn_cksaap.iloc[test])
    print(accuracy_score(true_labels, predictions))
    print(confusion_matrix(true_labels, predictions))
    pred_prob = svm_model.predict_proba(X_trn_cksaap.iloc[test])
    fpr, tpr, thresholds = metrics.roc_curve(true_labels, pred_prob[:,1], pos_label=1)
    print('AUC = ', metrics.auc(fpr, tpr))

"""### Imbalance solving"""

from imblearn.over_sampling import RandomOverSampler
from imblearn.over_sampling import ADASYN
from imblearn.over_sampling import BorderlineSMOTE
from imblearn.over_sampling import SMOTE
from collections import Counter

ros = BorderlineSMOTE()
# Re-train
cv_scores_ros = []
for train, test in kfold.split(X_trn_cksaap, y_trn):
    train_x, train_y = X_trn_cksaap.iloc[train], y_trn.iloc[train]
    X_ros, y_ros = ros.fit_resample(train_x, train_y)
    print('Resampled dataset shape %s' % Counter(y_ros))
    svm_model = libsvm_model()   
    ## evaluate the model
    svm_model.fit(X_ros, y_ros)
    # evaluate the model
    true_labels = np.asarray(y_trn.iloc[test])
    predictions = svm_model.predict(X_trn_cksaap.iloc[test])
    # print(accuracy_score(true_labels, predictions))
    print(confusion_matrix(true_labels, predictions))
    cv_scores_ros.append(accuracy_score(true_labels, predictions))

print('Average accuracy: ', np.mean(cv_scores_ros))

"""### Adjust the classification threshold"""

def evaluate_threshold(threshold):
    print('Sensitivity:', tpr[thresholds > threshold][-1])
    print('Specificity:', 1 - fpr[thresholds > threshold][-1])