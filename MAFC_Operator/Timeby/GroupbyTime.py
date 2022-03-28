from MAFC_Operator.operator_base import Operator, operatorType, outputType


class GroupbyTime(Operator):
    def __init__(self):
        self.mapoper = {"max": 0, "min": 1, "count": 2, "mean": 3, "std": 4}

    def generateName(self,sourcecolumns,targetcolumn):
        Sname = "Source("
        for sc in sourcecolumns:
            sname = sc['name']
            Sname += sname
            Sname += ";"
        Sname += ")"
        Tname = "Target("
        for tc in targetcolumn:
            tname = tc['name']
            Tname += tname
            Tname += ";"
        Tname += ")"

        name = Sname + "_" + Tname
        return name

    def getType(self) -> operatorType:
        return operatorType.TimeGroupBy

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if len(targetColumns) != 1 or len(sourceColumns) == 1:
            return False

        if targetColumns[0]['type'] != outputType.Discrete or targetColumns[0]['type'] != outputType.Numeric:
            return  False
        datenum = 0
        for sc in sourceColumns:
            if sc['type'] != outputType.Discrete or sc['type'] != outputType.Date:
                return False
            if sc['type'] == outputType.Date:
                datenum += 1
        if datenum != 1:
            return False
        return True

    def processTrainingSet(self, dataset, sourceColumns, targetColumns):
        sname = []
        for sc in sourceColumns:
            sname.append(sc['name'])
        tname = targetColumns[0]['name']
        columndata = dataset.groupby(sname)[tname].agg(["max","min","count","mean","std"])
        thedata = columndata.compute()
        value = [i for i in thedata.values]
        key = [i for i in thedata.index]
        if len(value) != len(key):
            raise ("GroupBy Process Error!")
        self.data = {}
        for i in range(0,len(value)):
            self.data[key[i]] = value[i]
