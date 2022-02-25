from MAFC_Operator.Binary.binary import Binary
from MAFC_Operator.operator_base import outputType


class SubOperator(Binary):
    def __init__(self):
        pass

    def requiredInputType(self) -> outputType:
        return outputType.Numeric

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "SubOperator"

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        scolumnname = sourceColumns[0]['name']
        tcolumnname = targetColumns[0]['name']
        columndata = dataset[scolumnname] - dataset[tcolumnname]
        name = "SubOperator" + self.generateName(sourceColumns,targetColumns)
        newcolumn = {"name": name, "data": columndata}
        return newcolumn
