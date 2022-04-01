from MAFC_Operator.Unary.unary import Unary
from MAFC_Operator.operator_base import outputType


class StdOperator(Unary):
    def __init__(self):
        pass

    def requiredInputType(self) -> outputType:
        return outputType.Numeric

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def processTrainingSet(self, dataset, sourceColumns, targetColumns):

        columnname = sourceColumns[0]['name']
        self.meanval = dataset[columnname].mean().compute()
        self.stdval = dataset[columnname].std().compute()


    def getName(self) -> str:
        return "StdOperator"

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        columnname = sourceColumns[0]['name']
        name = "StdOperator(" + columnname + ")"
        if self.stdval == 0:
            return {"name":name,"data":None}
        def getstd(data, meanval, stdval):
            return (data - meanval) / stdval
        columndata = dataset[columnname].apply(getstd, meanval=self.meanval, stdval=self.stdval, meta=('getstd','i8'))
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(StdOperator, self).isMatch(dataset, sourceColumns, targetColumns):
            if sourceColumns[0]['type'] == outputType.Numeric:
                return True
        return False

    def getNumofBins(self) -> int:
        return -1