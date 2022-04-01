import math

import numpy as np
from dask_ml.model_selection import train_test_split

from Evaluation.FEvaluation.FEvaluation import FEvaluation
from logger.logger import logger
from Evaluation.Evaluation import evalutionScoringMethod
class InformationGainFilterEvaluator(FEvaluation):

    def __init__(self):
        super(InformationGainFilterEvaluator, self).__init__()
        self.valuesPerKey = {}

    def produceScore(self, analyzedDatasets, currentScore, oa, candidateAttributes):
        if candidateAttributes != None:
            #留坑
            analyzedDatasets["data"][candidateAttributes[0]] = candidateAttributes[1]

        bins = 10
        flag = super(InformationGainFilterEvaluator, self).discretizeColumns(analyzedDatasets, bins)
        self.valuesPerKey = {}
        X_train, X_test, y_train, y_test = train_test_split(analyzedDatasets["data"], analyzedDatasets["target"], test_size=0.3, shuffle=False)

        for cl in self.analycolumns:
            val = cl[1].compute().values

            for index, value in zip(y_test.index, y_test):
                indexlist = []
                indexlist.append(val[index])
                indexkey = tuple(indexlist)
                if self.valuesPerKey.get(indexkey) == None:
                    numofunique = analyzedDatasets["targetInfo"].getNumsOfUnique()
                    if numofunique == None:
                        logger.Error(analyzedDatasets["targetInfo"].getName(), "Discrete Column is not exist numsofunique")
                    self.valuesPerKey[indexkey] = list(np.zeros(numofunique))
                self.valuesPerKey[indexkey][value] += 1

        return self.calculateIG(X_train)


    def calculateIG(self, dataset):
        IG = 0.0
        for val in self.valuesPerKey.values():
            numOfInstances = sum(val)
            tempIG = 0
            for va in val:
                if va != 0:
                    tempIG += -((va / numOfInstances) * math.log10(va / numOfInstances))

            IG += (numOfInstances / len(dataset)) * tempIG
        return IG


    def needToRecalcScore(self) -> bool:
        return False

    def getEvalutionScoringMethod(self):
        return evalutionScoringMethod.InformationGain
