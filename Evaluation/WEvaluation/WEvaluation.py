import numpy as np
from Evaluation.Evaluation import *
from Evaluation.Classification.ClassificationResults import ClassificationResults
from properties.properties import theproperty
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.metrics import log_loss
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegressionCV
from dask_ml.wrappers import ParallelPostFit
from dask_ml.model_selection import train_test_split
from distributed import Client


class WEvaluation(Evaluation):
    def __init__(self):
        super(WEvaluation, self).__init__()

    def evaluationAsave(self):
        pass

    def ProduceClassifications(self, dataset, classifier):
        classificationresult = self.getClassifications(dataset, classifier)
        return classificationresult

    def runClassifier(self, classifiername, datadict):
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
        y_p = y_pred.compute()
        y_t = y_test.compute().values
        #y_t = [val[1] for val in y_t]
        client.close()
        return (y_t, y_p)

    def calculateAUC(self, evaluation):
        auc = roc_auc_score(evaluation[0], evaluation[1])
        return auc

    def calculateLoss(self, evaluation):
        one_hot = OneHotEncoder(sparse=False)
        y_true = [[i] for i in evaluation[0]]
        y_true = one_hot.fit_transform(y_true)
        y_pred = [[i] for i in evaluation[1]]
        y_pred = one_hot.fit_transform(y_pred)
        return log_loss(y_true, y_pred)


    def calculateFsocre(self, evaluation):
        return f1_score(evaluation[0], evaluation[1], average='macro')

    def getClassifications(self, dataset, classifier):
        evaluations = self.runClassifier(classifier, dataset)
        auc = self.calculateAUC(evaluations)
        loss = self.calculateLoss(evaluations)
        fmeasurevalue = self.calculateFsocre(evaluations)
        return ClassificationResults(auc, loss, fmeasurevalue)




