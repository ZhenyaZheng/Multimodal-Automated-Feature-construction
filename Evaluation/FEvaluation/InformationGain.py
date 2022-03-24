import math

from Evaluation.FEvaluation.FEvaluation import FEvaluation

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
        super(InformationGainFilterEvaluator, self).discretizeColumns(analyzedDatasets, bins)

        self.valuesPerKey = {}
        targetcolumn = analyzedDatasets['target']
        self.valuesPerKey = dict(targetcolumn.value_counts().compute())
        return self.calculateIG(analyzedDatasets["data"])


    def calculateIG(self, dataset):
        IG = 0.0
        numOfInstances = sum(self.valuesPerKey.values())
        tempIG = 0
        for val in self.valuesPerKey.values():
            if val != 0:
                tempIG += -((val / numOfInstances) * math.log10(val / numOfInstances))

        IG += (numOfInstances/len(dataset)) * tempIG
        return IG


    def needToRecalcScore(self) -> bool:
        return False

    def getEvalutionScoringMethod(self):
        return evalutionScoringMethod.InformationGain
