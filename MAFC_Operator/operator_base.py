from abc import abstractmethod
from enum import Enum
import numpy as np

class operatorType(Enum):
    Unary = 1
    Binary = 2
    GroupBy = 3
    TimeGroupBy = 4

class outputType(Enum):
    Numeric = 1
    Discrete = 2
    Date = 3

class Operator(object):

    @staticmethod
    def getColumnType(column ) -> outputType:
        if np.issubdtype(column.dtype,np.int64):
            return outputType.Discrete
        elif np.issubdtype(column.dtype,np.float64):
            return outputType.Numeric
        elif np.issubdtype(column.dtype,np.datetime64):
            return outputType.Date
        else:
            raise Exception('Unknown column type')

    def __init__(self):
        pass

    @abstractmethod
    def getName(self) -> str:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    @abstractmethod
    def getType(self) -> operatorType:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    @abstractmethod
    def getOutputType(self) -> outputType:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    @abstractmethod
    def processTrainingSet(self, dataset, sourceColumns, targetColumns):
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    @abstractmethod
    def generateColumn(self, dataset, sourceColumns, targetColumns) :
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    @abstractmethod
    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

operatorlist = ['Operator'] + [i for i in Operator.__subclasses__()]