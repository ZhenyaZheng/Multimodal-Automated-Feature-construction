from Evaluation.Evaluation import *
from Evaluation.FEvaluation.OperatorBasedAttributes import DatasetBasedAttributes
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
from logger.logger import logger
from properties.properties import theproperty


class FEvaluation(Evaluation):
    def __init__(self, datadict):
        super(FEvaluation, self).__init__()
        self.analycolumns = []

    def recalculateDatasetBasedFeatures(self,datadict):
        pass

    def getType(self):
        return self.evalutionType.Filte

    @abstractmethod
    def needToRecalcScore(self) -> bool:
        pass

    def discretizeColumns(self,datadict):
        pass

    def initFEvaluation(self,columntoanalyze):
        self.analycolumns = columntoanalyze


