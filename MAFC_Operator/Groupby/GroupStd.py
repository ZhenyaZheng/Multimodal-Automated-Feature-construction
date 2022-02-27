from MAFC_Operator.Groupby.groupby import Groupby
from MAFC_Operator.operator_base import outputType


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

        def getstd(df, sourceColumns):
            sname = [sc['name'] for sc in sourceColumns]
            data = df[sname]
            columndata = []
            for i, j in enumerate(data.iterrows()):
                key = tuple(j[1].values)
                columndata.append(self.data[key][oper])
            return columndata

        columndata = dataset.map_partitions(getstd, sourceColumns, meta=('getstd', 'f8'))
        name = self.getName() + "(" + self.generateName(sourceColumns, targetColumns) + ")"
        newcolumn = {"name": name, "data": columndata}
        return newcolumn

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if super(Groupby,self).isMatch(dataset,sourceColumns,targetColumns):
            if targetColumns[0]['type'] == outputType.Discrete:
                return True
        return False