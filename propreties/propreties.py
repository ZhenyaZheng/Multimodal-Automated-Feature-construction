
class propreties:
    def __init__(self,numOfFolds = 4,randomSeed = 10,DiscretizerBinsNumber = 10 ):
        self.numOfFolds = numOfFolds #交叉验证折数
        self.randomSeed = randomSeed
        self.DiscretizerBinsNumber = DiscretizerBinsNumber #将实数离散化后的类数

