import copy
from utils import *
from Evaluation import *
from MAFC_Operator import OperatorManager
from properties.properties import properties, theproperty


def _FC_Noiter_(datadict ,unaryoperator_list : list,otheroperator_list:list):
    '''
    :param datadict:
    :param operator_list:
    :return:{"data":dask.dataframe,"Info":[ColumnInfo]}
    '''
    om = OperatorManager()
    #应用unary操作
    operators = om.UnaryOperator(datadict,unaryoperator_list)
    #将构造数据加入数据集
    om.GenerateAddColumnToData(datadict,operators)
    #应用聚集操作

    otheroperators = om.OtherOperator(datadict,otheroperator_list)
    #将构造数据加入数据集
    om.GenerateAddColumnToData(datadict,otheroperators)
    #newdata = datadict['data'].compute()
    return datadict['data']


def _FC_Iter_(datadict, unaryoperator_list : list,otheroperator_list : list,iternums : int):
    '''
    :param datadict: Dict[list(ColumnInfo), dask.dataframe]
    :param operator_list:
    :param iternums:
    :return:
    '''
    #初始化评估模型
    fevaluation = getEvaluation(theproperty.filter, datadict)
    wevaluation = getEvaluation(theproperty.wrapper, datadict)

    #进行初始评估
    wevaluation.evaluationAsave()
    currentscore = wevaluation.produceScore()
    logger.Info("Initial score is : ", currentscore)
    #计算
    currentclassifications = wevaluation.ProduceClassifications(datadict, theproperty.classifier)

    #复制数据集
    datasetcopy = copy.deepcopy(datadict)
    om = OperatorManager()
    # 应用unary操作
    operators = om.UnaryOperator(datasetcopy, unaryoperator_list)
    # 将构造数据加入数据集
    om.GenerateAddColumnToData(datasetcopy, operators)

    #初始化排序类
    rankerFilter = RankFilter()
    #不应该重复添加
    columnaddpreiter = None
    totalnumofwrapperevaluation = 0
    evaluationatts = 0
    chosenoperators = None
    toprankingoperators = None
    while iternums:
        #重新计算基本特征
        fevaluation.recalculateDatasetBasedFeatures(datasetcopy);
        #重新使用F计算分数
        om.reCalcFEvaluationScores(datasetcopy, operators, fevaluation)

        # 构造特征
        # 应用聚集操作
        otheroperators = om.OtherOperator(datasetcopy, otheroperator_list)

        #排序
        otheroperators = rankerFilter.rankAndFilter(otheroperators, columnaddpreiter)

        evaluationatts = 0
        chosenoperators = None
        toprankingoperators = []
        tempcurrentclassifications = currentclassifications
        #使用W计算分数,并行计算
        numofthread = theproperty.thread
        if numofthread == 1:
            for oop in otheroperators:
                if(oop.getFScore() != None and oop.getFScore() >= theproperty.fsocre and evaluationatts <= theproperty.maxevaluationattsperiter):
                    datacopy = copy.deepcopy(datasetcopy)
                    newcolumn = [om.generateColumn(datacopy, oop, False)]
                    wsocre = wevaluation.produceScore(datasetcopy, tempcurrentclassifications, oop, newcolumn)
                    oop.setWScore(wsocre)
                    evaluationatts += 1
                    if 0 < wsocre:
                        toprankingoperators.append(oop)

                    if(evaluationatts % 100 == 0):
                        logger.Info("evaluated ", evaluationatts, " attributes")
        else:
            pass
        # 筛选特征
        totalnumofwrapperevaluation += evaluationatts
        if chosenoperators == None:
            if toprankingoperators != None:
                chosenoperators = copy.deepcopy(toprankingoperators)
            else:
                logger.Info("No attributes are chosen,iteration over!")
                break

        om.GenerateAddColumnToData(datadict, chosenoperators)
        currentclassifications = wevaluation.ProduceClassifications(datadict, theproperty.classifier)
        wevaluation.evaluationAsave()
        iternums = iternums - 1
    return datadict['data']


def _FC_(datadict, isiteration: bool = False, iternums: int = 1, operatorbyself: dict = None, operatorignore: dict = None):
    '''
    :param datadict:
    :param isiteration:
    :param iternums:
    :param operatorbyself:
    :param operatorignore:
    :return:
    '''

    unaryoperatorlist = properties().unaryoperator
    otheroperatorlist = properties().otheroperator
    unaryoperator_list = unaryoperatorlist.copy()
    otheroperator_list = otheroperatorlist.copy()
    # 选择操作列表
    if operatorbyself is not None:
        unaryoperator_list = unaryoperator_list + operatorbyself['unary']
        otheroperator_list = otheroperator_list + operatorbyself['other']
    if operatorignore is not None:
        unaryoperator_list = list(set(unaryoperator_list) - set(operatorignore['unary']))
        otheroperator_list = list(set(otheroperator_list) - set(operatorignore['other']))

    if isiteration is False:
        df = _FC_Noiter_(datadict,unaryoperator_list,otheroperator_list)
    else:
        df = _FC_Iter_(datadict,unaryoperator_list,otheroperator_list,iternums)

    return df

def Merge_Data(image_data,text_data,tab_data):
    '''
    :param image_data:
    :param text_data:
    :param tab_data:
    :return:dask.dataframe
    '''
    if image_data is not None :
        if text_data is not None:
            data = image_data.merge(text_data)
            if tab_data is not None:
                data = data.merge(tab_data)
        elif tab_data is not None:
            data = image_data.merge(tab_data)
    else:
        if text_data is not None:
            data = text_data
            if tab_data is not None:
                data = data.merge(tab_data)
        elif tab_data is not None:
            data = tab_data
    data.name = theproperty.datasetname
    return data

def getDatadict(dataset):
    # image_fc,text_fc需要支持自定义构造
    image_fc = Image_FC(dataset.data_image)
    text_fc = Text_FC(dataset.data_text)
    ##合并image、text和tabular
    data = Merge_Data(image_fc, text_fc, dataset.data_tabular)
    datainfo = getInfo(data)
    datadict = {"data": data, "Info": datainfo}
    index = theproperty.targetindex
    datadict["target"] = datadict["data"].iloc[:, index]
    del datadict["data"][datadict["target"].name]
    datadict["targetInfo"] = datainfo.pop(-1)
    return datadict


def FC(dataset, isiteration: bool = False, iternums: int = 1,operatorbyself: list = None, operatorignore: list = None):
    '''
    :param operatorignore:
    :param operatorbyself:
    :param iternums: 迭代次数
    :param dataset:数据集
    :param isiteration: 是否进行迭代
    :return: dask.Dataframe
    '''
    datadict = getDatadict(dataset)
    df = _FC_(datadict, isiteration, iternums,operatorbyself,operatorignore)
    return df
