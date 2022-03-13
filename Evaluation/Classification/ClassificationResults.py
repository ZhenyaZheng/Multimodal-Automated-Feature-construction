

class ClassificationResults:

    def __init__(self, itemClassifications, auc, logloss, tprFprValues,
                recallPrecisionValues, fMeasureValuesPerRecall):
        self.itemClassifications = itemClassifications
        self.auc = auc
        self.logLoss = logloss
        self.tprFprValues = tprFprValues
        self.recallPrecisionValues = recallPrecisionValues
        self.fMeasureValuesPerRecall = fMeasureValuesPerRecall

    def getItemClassifications(self):
        return self.itemClassifications

    def getAuc(self):
        return self.auc

    def getLogLoss(self):
        return self.logLoss

    def getTprFprValues(self):
        return self.tprFprValues

    def getRecallPrecisionValues(self):
        return self.recallPrecisionValues

    def getFMeasureValuesPerRecall(self):
        return self.fMeasureValuesPerRecall
