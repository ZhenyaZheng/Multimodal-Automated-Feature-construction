import copy
import os

import parallel.parallel
from Serialize import serialize, deserialize
from utils import *
from Evaluation import *
from MAFC_Operator import OperatorManager
from properties.properties import properties, theproperty


def _FC_Noiter_(datadict ,unaryoperator_list: list, otheroperator_list: list):
    '''
    非迭代
    :param datadict:{"data":dask.dataframe.Dataframe,"Info":[ColumnInfo],"target":dask.dataframe.core.Series,"targetInfo":ColumnInfo}
    :param operator_list:[operatorname: str]
    :param otheroperator_list:[operatorname: str]
    :return:dask.dataframe.Dataframe
    '''
    try:
        om = OperatorManager()
        #应用unary操作
        operators = om.UnaryOperator(datadict,unaryoperator_list)
        #将构造数据加入数据集
        om.GenerateAddColumnToData(datadict,operators)
        #应用聚集操作
        otheroperators = om.OtherOperator(datadict,otheroperator_list)
        #将构造数据加入数据集
        om.GenerateAddColumnToData(datadict,otheroperators)
    except Exception as ex:
        logger.Error(f"_FC_Noiter_ error: {ex}", ex)
    #newdata = datadict['data'].compute()
    finally:
        return datadict['data']


def _FC_Iter_(datadict, unaryoperator_list: list, otheroperator_list: list, iternums :int):
    '''
    迭代
    :param datadict:{"data":dask.dataframe.Dataframe,"Info":[ColumnInfo],"target":dask.dataframe.core.Series,"targetInfo":ColumnInfo}
    :param operator_list:[operatorname: str]
    :param otheroperator_list:[operatorname: str]
    :param iternums:int
    :return:dask.dataframe.Dataframe
    '''
    #初始化评估模型
    try:
        fevaluation = getEvaluation(theproperty.filter, datadict)
        wevaluation = getEvaluation(theproperty.wrapper, datadict)

        #进行初始评估
        currentscore = wevaluation.produceScore(datadict, None, None, None)

        logger.Info("Initial score is : " + str(currentscore))
        #计算
        currentclassifications = wevaluation.ProduceClassifications(datadict, theproperty.classifier)
        wevaluation.evaluationAsave(currentclassifications)
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
        finalchosenops = operators
        iters = 1
        while iters <= iternums:
            #重新计算基本特征
            try:
                fevaluation.recalculateDatasetBasedFeatures(datasetcopy)
                # 构造特征
                # 应用聚集操作
                otheroperatorspath = theproperty.finalchosenopspath + "otheroperators" + str(iters)
                if os.path.isfile(otheroperatorspath):
                    otheroperators = deserialize(otheroperatorspath)
                else:
                    otheroperators = om.OtherOperator(datasetcopy, otheroperator_list)
                    # 重新使用F计算分数
                    otheroperators = list(set(otheroperators) - set(finalchosenops))
                    om.reCalcFEvaluationScores(datasetcopy, otheroperators, fevaluation)
                    #排序
                    otheroperators = rankerFilter.rankAndFilter(otheroperators, columnaddpreiter)
                    serialize(theproperty.finalchosenopspath + "otheroperators" + str(iters), otheroperators)
                evaluationatts = 0
                chosenoperators = None
                toprankingoperators = []
                tempcurrentclassifications = currentclassifications
                #使用W计算分数,并行计算
                numofthread = theproperty.thread

                def myevaluationfunc(oop):
                    if oop.getFScore() is not None and oop.getFScore() > theproperty.fsocre:
                        datacopy = copy.deepcopy(datasetcopy)
                        newcolumn = om.generateColumn(datacopy["data"], oop, False)
                        wscore = wevaluation.produceScore(datacopy, tempcurrentclassifications, oop, newcolumn)
                        oop.setWScore(wscore)
                        if 0 < wscore:
                            toprankingoperators.append(oop)
                        return [wscore]

                if numofthread == 1:
                    for oop in otheroperators:
                        if(oop.getFScore() != None and oop.getFScore() >= theproperty.fsocre and evaluationatts <= theproperty.maxevaluationattsperiter):
                            datacopy = copy.deepcopy(datasetcopy)
                            newcolumn = om.generateColumn(datacopy["data"], oop, False)
                            wscore = wevaluation.produceScore(datacopy, tempcurrentclassifications, oop, newcolumn)
                            oop.setWScore(wscore)
                            evaluationatts += 1
                            if 0 < wscore:
                                toprankingoperators.append(oop)

                            if(evaluationatts % 100 == 0):
                                logger.Info("evaluated " + str(evaluationatts) + " attributes, and time is " + str(datetime.datetime.now()))

                else:
                    paraevaluatedattrs = parallel.palallelForEach(myevaluationfunc, [oop for oop in otheroperators])
                    evaluationatts += len(paraevaluatedattrs)

                # 筛选特征
                totalnumofwrapperevaluation += evaluationatts
                if chosenoperators is None:
                    if len(toprankingoperators) > 0:
                        chosenoperators = copy.deepcopy(toprankingoperators)
                    else:
                        logger.Info("No attributes are chosen,iteration over!")
                        break
                finalchosenops += chosenoperators
                om.GenerateAddColumnToData(datasetcopy, chosenoperators)
                currentclassifications = wevaluation.ProduceClassifications(datasetcopy, theproperty.classifier)
                wevaluation.evaluationAsave(currentclassifications, iters, chosenoperators, totalnumofwrapperevaluation, False)

            except Exception as ex:
                logger.Error(f"calculateWsocre while error!{ex}")
            finally:
                iters += 1

    except Exception as ex:
        logger.Error(f"calculateWsocre error!{ex}")
    finally:
        serialize(theproperty.finalchosenopspath + "finalchosenops", finalchosenops)
        return datasetcopy['data']


def _FC_(datadict, isiteration: bool = False, iternums: int = 1, operatorbyself: dict = None, operatorignore: dict = None):
    '''

    :param datadict: {"data":dask.dataframe.Dataframe,"Info":[ColumnInfo],"target":dask.dataframe.core.Series,"targetInfo":ColumnInfo}
    :param isiteration: bool
    :param iternums: int
    :param operatorbyself: {"text":[],"tabular":[],"image":[]}自定义操作
    :param operatorignore:{"text":[],"tabular":[],"image":[]}忽略的操作
    :return:dask.dataframe.Dataframe
    '''
    try:
        unaryoperatorlist = properties().unaryoperator
        otheroperatorlist = properties().otheroperator
        unaryoperator_list = unaryoperatorlist.copy()
        otheroperator_list = otheroperatorlist.copy()
        # 选择操作列表
        if operatorbyself is not None and operatorbyself.get("tabular") is not None:
            unaryoperator_list = unaryoperator_list + operatorbyself["tabular"]['unary']
            otheroperator_list = otheroperator_list + operatorbyself["tabular"]['other']
        if operatorignore is not None and operatorignore.get("tabular") is not None:
            unaryoperator_list = list(set(unaryoperator_list) - set(operatorignore["tabular"]['unary']))
            otheroperator_list = list(set(otheroperator_list) - set(operatorignore["tabular"]['other']))
        df = None

        if isiteration is False:
            df = _FC_Noiter_(datadict, unaryoperator_list, otheroperator_list)
        else:
            df = _FC_Iter_(datadict, unaryoperator_list, otheroperator_list, iternums)
    except Exception as ex:
        logger.Error(f'Failed in func "_FC_" with exception: {ex}')
        saveDateFrame(df, datadict["data"].name)

    return df

def FC(dataset, isiteration: bool = False, iternums: int = 1,operatorbyself: dict = None, operatorignore: dict = None):
    '''
    :param operatorignore:{"text":[],"tabular":[],"image":[]}自定义操作
    :param operatorbyself:{"text":[],"tabular":[],"image":[]}忽略的操作
    :param iternums: 迭代次数
    :param dataset:数据集
    :param isiteration: 是否进行迭代
    :return: dask.dataframe.Dataframe
    '''
    datadict = getDatadict(dataset, operatorbyself, operatorignore)
    df = _FC_(datadict, isiteration, iternums, operatorbyself, operatorignore)
    return df

def generateTestData(datadict):
    operators = deserialize(theproperty.finalchosenopspath)
    om = OperatorManager()
    om.GenerateAddColumnToData(datadict, operators)
    saveDateFrame(datadict["data"], datadict["data"].name)

