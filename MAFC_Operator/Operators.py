from MAFC_Operator.operator_base import Operator
class Operators:

    def __init__(self,sourceColumns,targetcolumn,operator,secondoperator):#将构造数据加入数据集.
        self.sourceColumns = sourceColumns
        self.targetColumns = targetcolumn
        self.operators = operator
        self.secondoperators = secondoperator
        self.filterscore = 0.0
        self.wrapperscore = 0.0

    def GetName(self):
        str = "{sources:["
        for columnname in self.sourceColumns:
            str = str + columnname.GetName()
            str = str + ","
        str = str + "];"
        str = str + "Targets:["
        if self.targetColumns is not None:
            for columnname in self.targetColumns :
                str = str + columnname.GetName()
                str = str + ","
        str = str + "];"
        str = str + self.operators.getName()
        if self.secondoperators is not None:
            str = str + ","
            str = str + self.secondoperators.getName()
        str = str + "}"
        return str
