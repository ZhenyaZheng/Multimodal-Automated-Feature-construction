from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType
from logger.logger import logger

class GroupCount(Groupby):
    def __init__(self):
        super(GroupCount, self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Discrete

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "GroupCount"

    def processTrainingSet(self, dataset, sourceColumns: list, targetColumns: list):
        sname = []
        for sc in sourceColumns:
            sname.append(sc['name'])
        tname = targetColumns[0]['name']
        columndata = dataset.groupby(sname)[tname].agg("count")
        thedata = columndata.compute()
        value = [i for i in thedata.values]
        key = [i for i in thedata.index]
        if len(value) != len(key):
            logger.Info("GroupBy Process Error, len(value) != len(key)!")
            return
        self.data = {}
        for i in range(0, len(value)):
            self.data[key[i]] = value[i]


    def generateColumn(self, dataset, sourceColumns, targetColumns):

        def getcount(df, sourceColumns, datadict):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            key = tuple(data.values)
            if datadict.get(key) is None:
                #raise()
                #logger.Info("GroupCount:self.data is not init")
                return 0
            return datadict[key]

        columndata = dataset.apply(getcount, sourceColumns=sourceColumns, datadict=self.data, meta=('getcount', 'float'), axis=1)
        name = self.getName() + "(" + self.generateName(sourceColumns, targetColumns) + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(GroupCount, self).isMatch(dataset, sourceColumns, targetColumns):
            if targetColumns[0]['type'] == outputType.Numeric:
                return True
        return False