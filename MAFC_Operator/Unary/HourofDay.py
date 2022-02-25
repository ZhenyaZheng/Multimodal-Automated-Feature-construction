from MAFC_Operator.Unary.unary import Unary
from MAFC_Operator.operator_base import outputType


class HourofDay(Unary):
    def __init__(self):
        super(HourofDay, self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Date

    def processTrainingSet(self, dataset, sourceColumns, targetColumns):
        pass

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        '''
        :param sourceColumns:{'name':列名,'type':outputType}
        :param targetColumns:{'name':列名,'type':outputType}
        :return: dask.dataframe.series
        '''
        columnname = sourceColumns[0]['name']

        def gethour(dates):
            return [date.time().hour for date in dates]

        columndata = dataset[columnname].map_partitions(gethour, meta=('gethour', 'i8'))
        name = "HourofDay(" + columnname + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(HourofDay, self).isMatch(dataset,sourceColumns,targetColumns):
            if sourceColumns[0]['type'] == outputType.Date:
               return True
        return False

    def getNumofBins(self) -> int:
        return 24

    def getName(self):
        return "HourofDay"

    def getOutputType(self) -> outputType:
        return outputType.Discrete
