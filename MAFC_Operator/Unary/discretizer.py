from MAFC_Operator.Unary.unary import Unary
from MAFC_Operator.operator_base import outputType
from propreties.propreties import *

class Discretizer(Unary):
    def __init__(self, upperbound=propreties().DiscretizerBinsNumber):
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

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        columnname = sourceColumns[0]['name']
        def getdiscretizer(datas):
            return [int((data - self.min_float) // self.therange) for data in datas]
        columndata = dataset[columnname].map_partitions(getdiscretizer,meta = ('getdiscretizer','i8'))

        name = "Discretizer(" + columnname + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(Discretizer, self).isMatch(dataset,sourceColumns,targetColumns):
            if sourceColumns[0]['type'] == outputType.Numeric:
                return True
        return False

    def getIndex(self,value):
        for i in range(0, len(self.upperbound)):
            if self.upperbound[i] > value:
                return i
        return len(self.upperbound - 1)

    def getNumofBins(self) -> int:
        return len(self.upperbound)