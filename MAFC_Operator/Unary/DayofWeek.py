from MAFC_Operator.Unary.unary import Unary
from MAFC_Operator.operator_base import outputType


class DayofWeek(Unary):
    def __init__(self):
        super(DayofWeek, self).__init__()

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

        def getweek(dates):
            return [date.weekday() for date in dates]

        columndata = dataset[columnname].map_partitions(getweek, meta=('getweek', 'i8'))
        name = "DayofWeek(" + columnname + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(DayofWeek, self).isMatch(dataset,sourceColumns,targetColumns):
            if sourceColumns[0]['type'] == outputType.Date:
               return True
        return False

    def getNumofBins(self) -> int:
        return 7

    def getName(self):
        return "DayofWeek"

    def getOutputType(self) -> outputType:
        return outputType.Discrete
