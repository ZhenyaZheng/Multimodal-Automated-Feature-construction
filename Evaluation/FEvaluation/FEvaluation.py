from Evaluation.Evaluation import *



class FEvaluation(Evaluation):
    def __init__(self):
        super(FEvaluation, self).__init__()
        self.analycolumns = []

    @abstractmethod
    def recalculateDatasetBasedFeatures(self,datadict):
        pass

    def getType(self):
        return self.evalutionType.Filte

    @abstractmethod
    def needToRecalcScore(self) -> bool:
        pass

    def discretizeColumns(self, datadict, bins):
        for acs in self.analycolumns:
            pass


    def initFEvaluation(self,columntoanalyze):
        self.analycolumns = columntoanalyze




