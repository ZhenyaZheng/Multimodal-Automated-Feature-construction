from MAFC_Operator.Unary.unary import Unary
from MAFC_Operator.operator_base import outputType
from properties.properties import *

class Discretizer(Unary):
    def __init__(self, upperbound=theproperty.DiscretizerBinsNumber):
        self.upperbound = upperbound

    def requiredInputType(self) -> outputType:
        return outputType.Numeric

    def getOutputType(self) -> outputType:
        return outputType.Discrete

    def processTrainingSet(self, dataset, sourceColumns, targetColumns):

        columnname = sourceColumns[0]['name']
        self.max_float = dataset[columnname].max().compute()
        self.min_float = dataset[columnname].min().compute()
        diff = self.max_float - self.min_float
        #print(diff)
        self.therange = diff // self.upperbound


    def getName(self) -> str:
        return "Discretizer"

    def generateColumn(self, dataset, sourceColumns, targetColumns):
        columnname = sourceColumns[0]['name']
        def getdiscretizer(data, min_float, therange):
            if therange == 0:
                return 0
            return int((data - min_float) // therange)
        columndata = dataset[columnname].apply(getdiscretizer, min_float=self.min_float, therange=self.therange, meta=('getdiscretizer', 'i8'))

        name = "Discretizer(" + columnname + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(Discretizer, self).isMatch(dataset, sourceColumns, targetColumns):
            if sourceColumns[0]['type'] == outputType.Numeric:
                return True
        return False

    def getNumofBins(self) -> int:
        return self.upperbound