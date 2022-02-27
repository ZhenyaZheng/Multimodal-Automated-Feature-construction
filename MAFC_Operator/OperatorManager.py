from MAFC_Operator import operatorType
from MAFC_Operator.Combination import Combination
from MAFC_Operator.Operators import Operators

class OperatorManager:
    def __init__(self):
        pass

    def UnaryOperator(self, data):
        '''
        转化操作
        :return:
        '''
        operators = self.getOperators(data)

    def GenerateAddColumnToData(self):
        pass

    def OtherOperator(self):
        pass

    def getCombination(self, attributes:list, numsofcombination):
        comb = Combination(len(attributes), numsofcombination)
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

    def overlapexists(self,sources,target):
        pass

    def getUnaryOperatorList(self):
        pass

    def getOperators(self, data, operatorlist, maxcombinations,includeattributes = None):
        '''
        :param includeattributes:
        :param operatorlist:
        :param data:
        :return:the list of Operators
        '''
        isunaryoperator = True
        if (len(operatorlist) > 0 and operatorlist[0].getType() != operatorType.Unary):
            isunaryoperator = False

        if includeattributes == None:
            includeattributes = []
        theoperators = []
        i = maxcombinations
        while i > 0:
            attributecombination = self.getCombination(list(data.columns),i)
            for ac in attributecombination:
                if len(includeattributes) > 0:
                    thecolumn = ac.copy()
                    thecolumn = list(set(thecolumn) & set(includeattributes))
                    if len(thecolumn) == 0:
                        continue
                for op in operatorlist:
                    if(op.isMatch(data,ac,[])):
                        newops = Operators(ac,[],self.getOperator(op),None)
                        theoperators.append(newops)

                    for tc in list(data.columns):
                        if self.overlapexists(ac,tc):
                            continue
                        thecolumn = []
                        thecolumn.append(tc)
                        if(op.isMatch(data,ac,thecolumn)):
                            ops = Operators(ac,thecolumn,self.getOperator(op),None)
                            theoperators.append(ops)
        addoperators = []
        for os in theoperators:
            if os.getOperator().getType() != operatorType.Unary:
                for oper in self.getUnaryOperatorList():
                    if(oper.getType() == os.getOperator().getOutputType()):
                        addops = Operators(os.sourceColumns,os.targetColumns,os.operators,oper)
                        addoperators.append(addops)
        theoperators = theoperators + addoperators
        return theoperators
