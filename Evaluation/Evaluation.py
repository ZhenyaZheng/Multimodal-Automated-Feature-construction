from abc import abstractmethod
from enum import Enum


class evalutionType(Enum):
    Filte = 0
    Wrapper = 1


class evalutionScoringMethod(Enum):
    AUC = 1
    InformationGain = 2
    ProbDiff = 3
    LogLoss = 4
    ClassifierProbability = 5


class Evaluation:
    def __init__(self):
        self.evalutionType = evalutionType
        self.evalutionScoringMethod = evalutionScoringMethod

    @abstractmethod
    def produceScore(self, Datadict, currentScore, oa, candidateAttributes):
        pass

    @abstractmethod
    def getType(self):
        pass

    @abstractmethod
    def getEvalutionScoringMethod(self):
        pass
