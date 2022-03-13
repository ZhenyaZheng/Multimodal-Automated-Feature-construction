import dask
from MAFC_Operator import *
import dask
from Evaluation import *
from MAFC_Operator import OperatorManager
from properties.properties import properties


def Image_FC(image_data):
    '''

    :param image_data:
    :return: dask.Dataframe
    '''
    if image_data is None:
        return None


def Text_FC(text_data):
    '''
    :param text_data:
    :return: dask.Dataframe
    '''
    if text_data is None:
        return None

def getInfo(data):
    info = []
    for i in data:
        name = i
        if data[name].dtype == "datetime64[ns]":
            columninfo = ColumnInfo(None, None, None, name, False, outputType.Date)
        elif data[name].dtype == "float64":
            columninfo = ColumnInfo(None, None, None, name, False, outputType.Numeric)
        elif data[name].dtype == "int64":
            lensofvalues = len(data[name].value_counts().compute())
            if lensofvalues >= 100:
                columninfo = ColumnInfo(None, None, None, name, False, outputType.Numeric)
            else :
                columninfo = ColumnInfo(None, None, None, name, False, outputType.Discrete,lensofvalues)
        elif data[name].dtype == "object":
            seriesdict = {}
            dictnum = 0
            datavalues = data[name].value_counts().compute()
            for thekey in datavalues.keys():
                seriesdict[thekey] = dictnum
                dictnum += 1
            #data[name].compute()
            data[name] = data[name].replace(to_replace = seriesdict)
            data[name].astype("int32")
            columninfo = ColumnInfo(None, None, None, name, False, outputType.Discrete,len(seriesdict))
        elif data[name].dtype == "bool":
            data[name] = data[name].replace({"False": 0, "True": 1, "false": 0, "true": 1})
            #data[name].compute()
            data[name].astype("int32")
            columninfo = ColumnInfo(None, None, None, name, False, outputType.Discrete,2)
        info.append(columninfo)
    #newdata = data.compute()
    print("getInfo complete")
    return info

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
    newdata = datadict['data'].compute()
    return datadict

def _FC_Iter_(datadict ,unaryoperator_list : list,otheroperator_list : list,iternums : int):
    '''
    :param data:
    :param operator_list:
    :param iternums:
    :return:
    '''
    #初始化评估模型
    F_evaluation = FEvaluation()
    W_evaluation = WEvaluation()

    #进行初始评估
    W_evaluation.evaluationAsave()
    currentscore = W_evaluation.PredictScore()

    currentclassifications = W_evaluation.ProduceClassifications()

    #复制数据集
    datacopy = datadict.copy()

    om = OperatorManager()
    # 应用unary操作
    operators = om.UnaryOperator(datadict,unaryoperator_list)
    # 将构造数据加入数据集
    om.GenerateAddColumnToData(datadict,operators)

    #初始化排序类
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



    return datadict


def _FC_(data, isiteration: bool = False, iternums: int = 1, operatorbyself: dict = None, operatorignore: dict = None):
    '''
    :param data:
    :param isiteration:
    :param iternums:
    :param operatorbyself:
    :param operatorignore:
    :return:
    '''
    datainfo = getInfo(data)
    datadict = {"data": data, "Info": datainfo}
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
    return data




def FC(dataset, isiteration: bool = False, iternums: int = 1,operatorbyself: list = None, operatorignore: list = None):
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
    data = Merge_Data(image_fc,text_fc,dataset.data_tabular)
    df = _FC_(data, isiteration, iternums,operatorbyself,operatorignore)
    return df
