import os
from datetime import datetime
import numpy as np
from logger.logger import logger
from Evaluation.Evaluation import *
from Evaluation.Classification.ClassificationResults import ClassificationResults
from properties.properties import theproperty
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.metrics import log_loss
from sklearn.preprocessing import OneHotEncoder, label_binarize
from dask_ml.wrappers import ParallelPostFit
from dask_ml.model_selection import train_test_split
from distributed import Client
from MAFC_Operator.Operators import Operators

class WEvaluation(Evaluation):
    def __init__(self):
        super(WEvaluation, self).__init__()

    def evaluationAsave(self, currentresult: ClassificationResults, iteration=0, addatts:list[Operators]=None, nums=0, newfile=True):
        sb = ''
        if newfile:
            sb += "Iteration,Added_Attributes,LogLoss,AUC,F1Score"
            sb += ",Chosen_Attributes_FScore,Chosen_Attributes_WScore,Num_Of_Evaluated_Attributes_In_Iteration"
            sb += "Iteration_Completion_time"
            sb += os.linesep

        sb += str(iteration) + ","
        sb += '"['
        if addatts is not None:
            for ats in addatts:
                sb += ats.getName()
                sb += ","
        sb += ']",'
        sb += str(currentresult.getLogLoss()) + ","
        sb += str(currentresult.getAuc()) + ','
        sb += str(currentresult.getFMeasureValues()) + ","
        if addatts is not None:
            for ats in addatts:
                sb += ats.getFScore()
                sb += ","
            sb += ']","['
            for ats in addatts:
                sb += ats.getWScore()
                sb += ","
            sb += ']",'
        sb += str(nums) + ","
        date = datetime.now()
        sb += date.__str__()

        try:
            filepath = theproperty.resultfilepath + theproperty.datasetname + ".csv"
            if newfile:
                fw = open(filepath, "w")
            else:
                fw = open(filepath, "a")
            fw.write(sb + "\n")
            fw.close()
        except Exception as ex:
            logger.Error("IOException: " , ex)

    def ProduceClassifications(self, dataset, classifier):
        classificationresult = self.getClassifications(dataset, classifier)
        return classificationresult

    def runClassifier(self, classifiername, datadict):
        try:
            copydata = datadict["data"].copy()
            y = datadict["target"]
            if y.name in copydata.columns:
                del copydata[y.name]
            for name in copydata:
                if copydata[name].dtype not in ["int32", "int64", "float32", "float64", "bool"]:
                    del copydata[name]
            model = self.getClassifier(classifiername)
            client = Client()
            X_train, X_test, y_train, y_test = train_test_split(copydata, y, test_size=0.3, shuffle=False)
            #lens = (len(copydata), len(X_train), len(X_test), len(y_train), len(y_test))
            clf = ParallelPostFit(model, scoring="r2")
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            #y_pred_proba = clf.predict_proba(X_test)
            y_p = y_pred.compute()
            y_t = y_test.compute().values
            #y_t = [val[1] for val in y_t]
            client.close()
            return (y_t, y_p)
        except Exception as ex:
            logger.Error(f"runclassifier error", ex)
            return None

    def calculateAUC(self, evaluation):
        if evaluation is None:
            return 0
        try:
            multi = theproperty.targetmutil
            if multi:
                y_one_hot = label_binarize(evaluation[0], classes=np.arange(theproperty.targetclasses))
                ytrue_one_hot = label_binarize(evaluation[1], classes=np.arange(theproperty.targetclasses))
                auc = roc_auc_score(y_one_hot, ytrue_one_hot, multi_class='ovr')
            else:
                auc = roc_auc_score(evaluation[0], evaluation[1])
            return auc
        except Exception as ex:
            logger.Error(f"calculateAUC error", ex)
            return 0

    def calculateLoss(self, evaluation):
        if evaluation is None:
            return 0
        try:
            one_hot = OneHotEncoder(sparse=False)
            y_true = [[i] for i in evaluation[0]]
            y_true = one_hot.fit_transform(y_true)
            y_pred = [[i] for i in evaluation[1]]
            y_pred = one_hot.fit_transform(y_pred)
            return log_loss(y_true, y_pred)
        except Exception as ex:
            logger.Error(f"calculateLoss error", ex)
            return 0


    def calculateFsocre(self, evaluation):
        if evaluation is None:
            return 0
        try:
            return f1_score(evaluation[0], evaluation[1], average='macro')
        except Exception as ex:
            logger.Error(f"calculateFsocre error", ex)
            return 0

    def getClassifications(self, dataset, classifier):
        evaluations = self.runClassifier(classifier, dataset)
        auc = self.calculateAUC(evaluations)
        loss = self.calculateLoss(evaluations)
        fmeasurevalue = self.calculateFsocre(evaluations)
        return ClassificationResults(auc, loss, fmeasurevalue)




