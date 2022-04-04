from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType
from logger.logger import logger

class GroupStd(Groupby):
    def __init__(self):
        super(GroupStd,self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Discrete

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "GroupStd"

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        oper = self.mapoper["std"]

        def getstd(df, sourceColumns, thedatadict):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            key = tuple(data.values)
            if thedatadict.get(key) is None:
                logger.Error("Groupby.data is not init")
            return thedatadict[key][oper]

        keyname = self.getKeyname(sourceColumns, targetColumns)
        columndata = dataset.apply(getstd, sourceColumns=sourceColumns, thedatadict=self.getData(keyname), meta=('getstd', 'f8'), axis=1)
        name = self.getName() + "(" + self.generateName(sourceColumns, targetColumns) + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(GroupStd,self).isMatch(dataset, sourceColumns, targetColumns):
            if targetColumns[0]['type'] == outputType.Numeric:
                return True
        return False