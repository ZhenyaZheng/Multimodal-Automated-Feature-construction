from Evaluation.WEvaluation.WEvaluation import WEvaluation
from properties.properties import theproperty
from Evaluation.Evaluation import evalutionScoringMethod
from Evaluation.Classification.ClassificationResults import ClassificationResults


class AucWrapperEvaluation(WEvaluation):
    def __init__(self):
        pass

    def produceScore(self, analyzedatasets, currentscore: ClassificationResults, oa, candidateatt):
        if candidateatt != None:
            #留坑
            analyzedatasets["data"][candidateatt[0]] = candidateatt[1]
        evaluationresults = self.runClassifier(theproperty.classifier, analyzedatasets)
        auc = self.calculateAUC(evaluationresults)
        if currentscore != None:
            return auc - currentscore.getAuc()
        else:
            return auc

    def getEvalutionScoringMethod(self):
        return evalutionScoringMethod.AUC