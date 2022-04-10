from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType
from logger.logger import logger

class GroupMean(Groupby):
    def __init__(self):
        super(GroupMean, self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Discrete

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "GroupMean"

    def processTrainingSet(self, dataset, sourceColumns: list, targetColumns: list):
        sname = []
        for sc in sourceColumns:
            sname.append(sc['name'])
        tname = targetColumns[0]['name']
        columndata = dataset.groupby(sname)[tname].agg("mean")
        thedata = columndata.compute()
        value = [i for i in thedata.values]
        key = [i for i in thedata.index]
        if len(value) != len(key):
            logger.Error("GroupBy Process Error!")
        self.data = {}
        for i in range(0, len(value)):
            self.data[key[i]] = value[i]

    def generateColumn(self,dataset, sourceColumns, targetColumns):

        def getmean(df, sourceColumns, datadict):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            key = tuple(data.values)
            if datadict.get(key) is None:
                logger.Error("self.data is not init")
            return datadict[key]

        columndata = dataset.apply(getmean, sourceColumns=sourceColumns, datadict=self.data, meta=('getmean', 'float32'), axis=1)
        name = self.getName() + "(" + self.generateName(sourceColumns,targetColumns) + ")"
        newcolumn = {"name":name,"data":columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(GroupMean,self).isMatch(dataset,sourceColumns,targetColumns):
            if targetColumns[0]['type'] == outputType.Numeric:
                return True
        return False