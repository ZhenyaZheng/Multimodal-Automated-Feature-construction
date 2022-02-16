from typing import List
import dask as dk
from Dataset import Dataset
from MAFC_Operator.operator_base import Operator, outputType
from MAFC_Operator.operator_base import operatorType
class Unary(Operator):

    def __init__(self):
        super().__init__()
        self.abc: List[int]

    def getType(self) -> operatorType:
        return operatorType.Unary

    def requiredInputType(self) -> outputType:
        raise NotImplementedError("Unary is an abstract class")

    def isApplicable(self, dataset: Dataset, sourceColumns: List[dk.Series], targetColumns: List[dk.Series]) -> bool:

        if len(sourceColumns) != 1 or (targetColumns != None and len(targetColumns) != 0):

            return False
        else:
            return True

