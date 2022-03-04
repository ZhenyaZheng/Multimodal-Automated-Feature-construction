from abc import ABC

from MAFC_Operator import Operator, operatorType, outputType


class Groupby(Operator):
    def __init__(self):
        self.mapoper = {"max":0,"min":1,"count":2,"mean":3,"std":4}

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
        return operatorType.GroupBy

    def isMatch(self, dataset, sourceColumns, targetColumns) -> bool:
        if len(targetColumns) != 1:
            return False
        for sc in sourceColumns:
            if sc['type'] != outputType.Discrete:
                return False
        return True

    def processTrainingSet(self, dataset, sourceColumns: list, targetColumns: list):
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
