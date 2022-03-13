from Evaluation import FEvaluation
from Evaluation.FEvaluation.AttributeInfo import AttributeInfo
from Evaluation.FEvaluation.OperatorBasedAttributes import  OperatorBasedAttributes
from Evaluation.FEvaluation.DatasetAttributes import DatasetAttributes
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
from logger.logger import logger
from properties.properties import theproperty
from MAFC_Operator.operator_base import outputType


class MLFEvaluation(FEvaluation):
    def __init__(self, datadict):
        super(MLFEvaluation, self).__init__()
        self.classifier = None
        self.evalution = None
        self.datasetAttriutes = {}
        self.initBackModel(datadict)


    def initBackModel(self, datadict):
        logger.Info("Initializing Background Model for dataset " + datadict['data'].name)
        self.mla = MLAttributeManager()
        self.classifier = self.mla.getBackClassificationModel(datadict)

        self.dba = DatasetAttributes()
        self.datasetAttributes = self.dba.getDatasetBasedFeature(datadict, theproperty.classifier)

    def recalculateDatasetBasedFeatures(self, datadict):
        self.datasetAttributes = self.dba.getDatasetBasedFeature(datadict, theproperty.classifier)

    def setClassifier(self, classifier):
        self.classifier = classifier

    def setDataAttributes(self, datasetAttributes):
        self.datasetAttributes = datasetAttributes

    def setEvalution(self, evalution):
        self.evalution = evalution

    def produceScore(self, datadict, currentScore, oa, candidateAttribute):
        if self.classifier == None:
            logger.Error("Classifier is not initialized")
        oba = OperatorBasedAttributes()
        candidateAttributes = oba.getOperatorsBasedAttributes()
        for das in self.datasetAttributes:
            candidateAttributes[len(candidateAttributes)] = das
        classifierattribute = AttributeInfo("Classifier", outputType.Discrete, 0, 2)
        candidateAttributes[len(candidateAttributes)] = classifierattribute
        testInstances = self.mla.generateValuesData(candidateAttributes)
        testInstances.setClassIndex(len(testInstances) - 1)
        #初始化评估器
        #self.evalution = Evaluation(testInstances)

        #self.evalution.evaluateModel(self.classifier,testInstances)
        #预测
        #计算得分
        score = 0
        return score

    def needToRecalcScore(self) -> bool:
        return True

    def getEvalutionScoringMethod(self):
        return self.evalutionScoringMethod.ClassifierProbability

    def getClassifier(self):
        return self.classifier

    def getEvalution(self):
        return self.evalution