from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType


class GroupMin(Groupby):
    def __init__(self):
        super(GroupMin,self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Discrete

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "GroupMin"

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        oper = self.mapoper["min"]

        def getmin(df, sourceColumns):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            key = tuple(data.values)
            return self.data[key][oper]

        columndata = dataset.apply(getmin, sourceColumns=sourceColumns, meta=('getmin', 'f8'), axis=1)
        name = self.getName() + "(" + self.generateName(sourceColumns, targetColumns) + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(GroupMin,self).isMatch(dataset,sourceColumns,targetColumns):
            if targetColumns[0]['type'] == outputType.Numeric:
                return True
        return False