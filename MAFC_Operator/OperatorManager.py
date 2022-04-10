import copy
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from MAFC_Operator.Operators import Operators
from logger.logger import logger
from parallel import parallel
from properties.properties import theproperty
import pandas as pd
from MAFC_Operator.ColumnInfo import ColumnInfo
from MAFC_Operator.Combination import Combination
from MAFC_Operator.operator_base import operatorType
from MAFC_Operator.Binary import *
from MAFC_Operator.Unary import *
from MAFC_Operator.Groupby import *
class OperatorManager:
    def __init__(self):
        pass
    def addColumn(self, datadict, candidateatt):
        '''
        :param datadict:
        :param candidateatt:(name,data)
        :return:
        '''
        datadict["data"][candidateatt[0]] = candidateatt[1]
        datadict["Info"].append(candidateatt[2])

    def UnaryOperator(self, data,unaryoperatorlist):
        '''
        :param data: {"data":data,"Info":[ColumnInfo]}
        :param unaryoperatorlist: ["operator"]
        :return: [Operators]
        '''
        unaryoperators = [self.getUnaryOperator(unaryoperator) for unaryoperator in unaryoperatorlist]
        operators = self.getOperators(data, unaryoperators, theproperty.maxcombination)
        logger.Info("UnaryOperator complete")
        return operators

    def generateColumn(self, data, ops: Operators, needcompute: bool = False):
        '''
        :param data: data
        :param os:Operators
        :return: [values]
        '''
        operator = ops.getOperator()
        scdict = None
        if ops.sourceColumns is not None:
            scdict = [{"name": sc.getName(), "type": sc.getType()} for sc in ops.sourceColumns]
        tcdict = None
        if ops.targetColumns is not None:
            tcdict = [{"name": tc.getName(), "type": tc.getType()} for tc in ops.targetColumns]
        operator.processTrainingSet(data, scdict, tcdict)
        newcolumn = operator.generateColumn(data, scdict, tcdict)
        newcolumndata = newcolumn["data"].fillna(0)

        if needcompute == True:
            newcolumndata = newcolumndata.compute()
        if ops.getType() == outputType.Discrete:
            lensofvalues = ops.getNumofBins()
            columninfo = ColumnInfo(ops.sourceColumns, ops.targetColumns, operator, ops.getName(), False, ops.getType(), lensofvalues)
        else:
            columninfo = ColumnInfo(ops.sourceColumns, ops.targetColumns, operator, ops.getName(), False, ops.getType())
        return [ops.getName(), newcolumndata, columninfo]


    def GenerateAddColumnToData(self, datadict, operators):
        '''
        :param datadict:{"data":data,"Info":[ColumnInfo]}
        :param operators: [Operators]
        :return: Null
        '''
        lock = threading.Lock()
        def myfunc(ops, datadict):
            newcolumn = self.generateColumn(datadict["data"], ops)
            lock.acquire()
            self.addColumn(datadict, newcolumn)
            lock.release()

        threadnums = theproperty.thread
        if threadnums == 1:
            osnums = len(operators)
            num = 1
            for ops in operators:
                if num % 100 == 0:
                    print("this is ", num, " / ", osnums, " and time is ", datetime.datetime.now())
                num += 1
                newcolumn = self.generateColumn(datadict["data"], ops)
                self.addColumn(datadict, newcolumn)
        else:
            pool = ThreadPoolExecutor(max_workers=threadnums)
            maxops = len(operators)
            iterops = 0
            iterthread = 0
            threadlist = []
            for _ in range(min(threadnums, maxops)):
                threadlist.append(pool.submit(myfunc, operators[iterops], datadict))
                iterops += 1
            while iterops < maxops:
                for _ in range(threadnums):
                    if iterops >= maxops:
                        break
                    for _ in as_completed([threadlist[iterthread]]):
                        threadlist.append(pool.submit(myfunc, operators[iterops], datadict))
                        iterops += 1
                    iterthread += 1
                    if iterthread % 100 == 0:
                        logger.Info("this is " + str(iterthread) + " / " + str(maxops) + " and time is " + str(datetime.datetime.now()))
            while iterthread < maxops:
                for _ in as_completed([threadlist[iterthread]]):
                    iterthread += 1
        logger.Info("GenerateAddColumnToData complete")

    def OtherOperator(self, data, operatorlist):
        '''
        :param data: {"data":data,"Info":[ColumnInfo]}
        :param operatorlist: ["operator"]
        :return: [Operators]
        '''
        otheroperators = [self.getOtherOperator(operator) for operator in operatorlist]
        operators = self.getOperators(data, otheroperators, theproperty.maxcombination)
        logger.Info("OtherOperator complete")
        return operators

    def getCombination(self, attributes:list, numsofcombination):
        lengthofattribute = len(attributes)
        comb = Combination(lengthofattribute, numsofcombination)
        attributecombination = []
        while comb.hasMore():
            indices = comb.getNext()
            thecolumns = []
            for index in indices:
                thecolumns.append(attributes[index])
            attributecombination.append(thecolumns.copy())
        return attributecombination

    def getUnaryOperator(self,name):
        ob = eval(name + "()")
        return ob

    def getOtherOperator(self,name):
        if "Time" in name:
            names = name.split("_")
            ob = eval(names[0] + "(" + names[1] + ")")
        else:
            ob = eval(name + "()")
        return ob




    def getOperator(self,oper):
        if oper.getType() == operatorType.Unary:
            return self.getUnaryOperator(oper.getName())
        return self.getOtherOperator(oper.getName())

    def overlapexists(self, sources, target):
        '''
        :param sources:[ColumnInfo]
        :param target: ColumnInfo
        :return:bool
        '''
        #首先检查是否包含相同的
        if target in sources:
            return True
        #然后检查是否包含共享的
        sourcesans = []
        for source in sources:
            sourcesans.append(source)
            if source.getSourceColumns() is not None:
                for ansource in source.getSourceColumns():
                    if ansource not in sourcesans:
                        sourcesans.append(ansource)
            if source.getTargetColumns() is not None:
                for antarget in source.getTargetColumns():
                    if antarget not in sourcesans:
                        sourcesans.append(antarget)

        targetans = []
        targetans.append(target)
        if target.getSourceColumns() is not None:
            for ansource in target.getSourceColumns():
                if ansource not in targetans:
                    targetans.append(ansource)
        if target.getTargetColumns() is not None:
            for antarget in target.getTargetColumns():
                if antarget not in targetans:
                    targetans.append(antarget)
        overlap = len(set(sourcesans) & set(targetans)) > 0
        '''
        if overlap and len(targetans) > 1:
            raise ("target and sources overlap error!")
        '''
        return overlap

    def getUnaryOperatorList(self):
        operatorlist = []
        for op in theproperty.unaryoperator:
            operatorlist.append(self.getUnaryOperator(op))
        return operatorlist

    def getOperators(self, data, operatorlist, maxcombinations, includeattributes = None):
        '''
        :param includeattributes:[ColumnInfo]
        :param operatorlist:['operator']
        :param data:{"data":data,"Info":[ColumnInfo]}
        :return:the list of Operators
        '''

        if includeattributes == None:
            includeattributes = []
        theoperators = []
        i = maxcombinations
        while i > 0:
            attributecombination = self.getCombination(data["Info"], i)
            for ac in attributecombination:
                if len(includeattributes) > 0:
                    thecolumn = copy.deepcopy(ac)
                    thecolumn = list(set(thecolumn) & set(includeattributes))
                    if len(thecolumn) == 0:
                        continue
                for op in operatorlist:
                    if(op.isMatch(data["data"],[{"name":itac.getName(),"type":itac.getType()}for itac in ac],[])):
                        newops = Operators(ac, None, self.getOperator(op), None)
                        theoperators.append(newops)

                    for tc in list(data["Info"]):
                        if self.overlapexists(ac, tc):
                            continue
                        thecolumn = []
                        thecolumn.append(tc)
                        if(op.isMatch(data["data"],[{"name":itac.getName(),"type":itac.getType()}for itac in ac],[{"name":tc.getName(),"type":tc.getType()}for tc in thecolumn])):
                            ops = Operators(ac, thecolumn, self.getOperator(op), None)
                            theoperators.append(ops)
            i = i - 1
        addoperators = []
        for os in theoperators:
            if os.getOperator().getType() != operatorType.Unary:
                for oper in self.getUnaryOperatorList():
                    if(oper.getType() == os.getOperator().getOutputType()):
                        addops = Operators(os.sourceColumns, os.targetColumns, os.operators, oper)
                        addoperators.append(addops)
        theoperators = theoperators + addoperators
        return theoperators

    def reCalcFEvaluationScores(self, datadict, operators, fevaluation):
        if fevaluation.needToRecalcScore() is False:
            return
        else:
            self.calculateFsocre(datadict, fevaluation, operators)

    def calculateFsocre(self, datadict, fevaluation, operators: list[Operators]):
        numOfThread = theproperty.thread
        count = 0

        def myfunction(ops):
            datacopy = copy.deepcopy(datadict)
            newcolumn = self.generateColumn(datacopy["data"], ops)
            if newcolumn[1] is None or fevaluation is None:
                logger.Error("generate column or fevaluation error!")
            newfevaluation = copy.deepcopy(fevaluation)
            templist = [newcolumn]
            newfevaluation.initFEvaluation(templist)
            fsocre = newfevaluation.produceScore(datacopy, None, ops, newcolumn)
            ops.setFScore(fsocre)

        if numOfThread == 1:
            for ops in operators:
                datacopy = copy.deepcopy(datadict)
                count += 1
                if count % 1000 == 0:
                    logger.Info("analyzed " + str(count) + " attributes")
                newcolumn = self.generateColumn(datacopy["data"], ops)
                if newcolumn[1] is None or fevaluation is None:
                    logger.Error("generate column or fevaluation error!")
                newfevaluation = copy.deepcopy(fevaluation)

                templist = [newcolumn]

                newfevaluation.initFEvaluation(templist)
                fsocre = newfevaluation.produceScore(datacopy, None, ops, newcolumn)
                ops.setFScore(fsocre)
        else:
            parallel.ParallelForEachShare(myfunction, [ops for ops in operators])

