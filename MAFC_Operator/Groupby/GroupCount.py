from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType


class GroupCount(Groupby):
    def __init__(self):
        super(GroupCount,self).__init__()

    def requiredInputType(self) -> outputType:
        return outputType.Discrete

    def getOutputType(self) -> outputType:
        return outputType.Numeric

    def getName(self) -> str:
        return "GroupCount"

    def generateColumn(self,dataset, sourceColumns, targetColumns):
        oper = self.mapoper["count"]
        def getcount(df, sourceColumns):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            columndata = []
            for i, j in enumerate(data.iterrows()):
                key = tuple(j[1].values)
                columndata.append(self.data[key][oper])
            return columndata

        columndata = dataset.map_partitions(getcount, sourceColumns, meta=('getcount', 'f8'))
        name = self.getName() + "(" + self.generateName(sourceColumns, targetColumns) + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(GroupCount,self).isMatch(dataset,sourceColumns,targetColumns):
            if targetColumns[0]['type'] == outputType.Numeric:
                return True
        return False