
class properties:
    def __init__(self):
        '''
        :param
        :param
        :param
        :param
        :param
        :param
        :param
        :param
        :param

        '''
        self.unaryoperator = ['DayofWeek','Discretizer','HourofDay','IsWeekend','StdOperator']
        self.otheroperator = ['AddOperator','SubOperator','MultiOperator','DivisOperator','GroupMax','GroupMean','GroupMin','GroupStd','GroupCount']
        self.DiscretizerBinsNumber = 10 #将实数离散化后的类数
        self.maxcombination = 2
        self.classifier = 'RandomForest'
        self.datasetlocation = "data/datasets/"
        self.filter = "MLFEvaluation"
        self.wrapper = "AucWrapperEvaluation"
        self.thread = 1
        self.fsocre = 0.001
        self.maxevaluationattsperiter = 15000
        self.backmodelpath = "data/model/"
        self.datasetname = "dataset"
        self.classifiersforMLAttributes = ["RandomForest"]
        self.targetindex = -1
        self.image_path = None
        self.resultfilepath = "data/result/"
theproperty = properties()