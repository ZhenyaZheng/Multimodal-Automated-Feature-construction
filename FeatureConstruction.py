from Dataset import Dataset
import dask
from Evaluation import *
from MAFC_Operator import *

def Image_FC(image_data):
    '''

    :param image_data:
    :return: dask.Dataframe
    '''
    pass


def Text_FC(text_data):
    '''
    :param text_data:
    :return: dask.Dataframe
    '''
    pass


def _FC_Noiter_(data ,operator_list : list):
    '''
    :param data:
    :param operator_list:
    :return:
    '''

    om = OperatorManager()
    #应用unary操作
    om.UnaryOperator()
    #将构造数据加入数据集
    om.GenerateAddColumnToData()
    #应用聚集操作
    om.OtherOperator()
    #将构造数据加入数据集
    om.GenerateAddColumnToData()

    return data

def _FC_Iter_(data ,operator_list : list,iternums : int):
    '''
    :param data:
    :param operator_list:
    :param iternums:
    :return:
    '''
    F_evaluation = FEvaluation()
    W_evaluation = WEvaluation()

    W_evaluation.evaluationAsave()
    currentscore = W_evaluation.PredictScore()

    currentclassifications = W_evaluation.ProduceClassifications()

    #复制数据集
    datacopy = data.copy()

    om = OperatorManager()
    # 应用unary操作
    om.UnaryOperator()
    # 将构造数据加入数据集
    om.GenerateAddColumnToData()

    rankerFilter = RankFilter()

    while iternums:
        #重新计算基本特征
        F_evaluation.reCalcDataBasedFeatures();
        #重新使用F计算分数
        om.reCalcFEvaluationScores()

        # 构造特征
        # 应用聚集操作
        otheroperator = om.OtherOperator()

        #排序
        otheroperator = rankerFilter.rankAndFilter(otheroperator)

        #使用W计算分数
        for i in otheroperator:
            W_evaluation.PredictScore()

        # 筛选特征



        iternums = iternums - 1



    return data


def _FC_(data, isiteration: bool = False, iternums: int = 1, operatorbyself: list = None, operatorignore: list = None):
    '''
    :param data:
    :param isiteration:
    :param iternums:
    :param operatorbyself:
    :param operatorignore:
    :return:
    '''

    from MAFC_Operator.operator_base import operatorlist
    # 选择操作列表
    operator_list = operatorlist.copy()
    if operatorbyself is not None:
        operator_list = operator_list + operatorbyself
    if operatorignore is not None:
        operator_list = list(set(operator_list) - set(operatorignore))

    if isiteration is False:
        df = _FC_Noiter_(data,operator_list)
    else:
        df = _FC_Iter_(data,operator_list,iternums)

    return df


def FC(dataset: Dataset, isiteration: bool = False, iternums: int = 1,operatorbyself: list = None, operatorignore: list = None):
    '''
    :param operatorignore:
    :param operatorbyself:
    :param iternums: 迭代次数
    :param dataset:数据集
    :param isiteration: 是否进行迭代
    :return: dask.Dataframe
    '''
    #image_fc,text_fc需要支持自定义构造
    image_fc = Image_FC(dataset.data_image)
    text_fc = Text_FC(dataset.data_text)
    ##合并image、text和tabular
    data = dask.Dataframe()
    df = _FC_(data, isiteration, iternums,operatorbyself,operatorignore)
    return df
