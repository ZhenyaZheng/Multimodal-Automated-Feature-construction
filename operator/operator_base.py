
from enum import Enum
from typing import List

import dask as dk
import numpy as np
from Dataset import Dataset


class operatorType(Enum):
    Unary = 1
    Binary = 2
    GroupByThen = 3
    TimeBasedGroupByThen = 4

class outputType(Enum):
    Numeric = 1
    Discrete = 2
    Date = 3

class Operator:

    @staticmethod
    def getSeriesType(column ) -> outputType:
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

    def getName(self) -> str:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    def getType(self) -> operatorType:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    def getOutputType(self) -> outputType:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    def processTrainingSet(self, dataset: Dataset, sourceColumns: dk.Series, targetColumns):
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    def generate(self, dataset: Dataset, sourceColumns: dk.Series, targetColumns: list) -> dk.Series:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")

    def isApplicable(self, dataset: Dataset, sourceColumns: List[dk.Series], targetColumns: List[dk.Series]) -> bool:
        raise NotImplementedError("Abstract class Operator shouldn't instanced directly")