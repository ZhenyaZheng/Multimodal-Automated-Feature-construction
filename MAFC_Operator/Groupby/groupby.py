from abc import ABC
from logger.logger import logger
from MAFC_Operator import Operator, operatorType, outputType


class Groupby(Operator):

    data = {}
    isTrain = {}
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
        keyname = self.getKeyname(sourceColumns, targetColumns)
        if Groupby.isTrain.get(keyname) is None:
            Groupby.isTrain[keyname] = False
        if Groupby.isTrain[keyname] is True:
            return
        columndata = dataset.groupby(sname)[tname].agg(["max", "min", "count", "mean", "std"])
        thedata = columndata.compute()
        value = [i for i in thedata.values]
        key = [i for i in thedata.index]
        if len(value) != len(key):
            raise ("GroupBy Process Error!")
        Groupby.data[keyname] = {}
        for i in range(0, len(value)):
            Groupby.data[keyname][key[i]] = value[i]
        Groupby.isTrain[keyname] = True

    def getData(self, keyname):
        if Groupby.data.get(keyname) is None:
            logger.Error("Groupby.data" + keyname + " is not init")
        return Groupby.data[keyname]

    def getKeyname(self, sourceColumns, targetColumns):
        keyname = ""
        for sc in sourceColumns:
            keyname += sc['name']
        for tc in targetColumns:
            keyname += tc['name']
        return keyname