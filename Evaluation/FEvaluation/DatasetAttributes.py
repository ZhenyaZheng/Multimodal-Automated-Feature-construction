import copy
import numpy as np
import pandas as pd
import scipy
import scipy.stats
from Evaluation.FEvaluation.AttributeInfo import AttributeInfo
from Evaluation.WEvaluation.AucWrapperEvaluation import AucWrapperEvaluation
from MAFC_Operator.operator_base import outputType
from MAFC_Operator.Unary.discretizer import Discretizer
from Evaluation.FEvaluation.InformationGain import InformationGainFilterEvaluator
from logger.logger import logger
from properties.properties import theproperty
from Evaluation.FEvaluation.StatisticOperation import StatisticOperation

class DatasetAttributes:

    def __init__(self):
        #   数据集的一些基本特征
        self.numOfInstances: float
        self.numOfFeatures: float
        self.numOfNumericAttributes: float
        self.numOfDiscreteAttributes: float
        self.ratioOfNumericAttributes: float
        self.ratioOfDiscreteAttributes: float
        

        # 离散特征
        self.maxNumberOfDiscreteValuesPerAttribute: float
        self.minNumberOfDiscreteValuesPerAttribute: float
        self.avgNumOfDiscreteValuesPerAttribute: float
        self.stdNumOfDiscreteValuesPerAttribute: float

        # 数据集的统计学特征
        self.FMeasureValues: float
        self.logLossValues: float
        self.aucValues: float

        # 交叉熵信息
        self.maxIGVal: float
        self.minIGVal: float
        self.avgIGVal: float
        self.stdIGVal: float

        self.discreteAttsMaxIGVal: float
        self.discreteAttsMinIGVal: float
        self.discreteAttsAvgIGVal: float
        self.discreteAttsStdIGVal: float

        self.numericAttsMaxIGVal: float
        self.numericAttsMinIGVal: float
        self.numericAttsAvgIGVal: float
        self.numericAttsStdIGVal: float

        # 相关性信息
        self.maxPairedTTestValueForNumericAttributes: float
        self.minPairedTTestValueForNumericAttributes: float
        self.avgPairedTTestValueForNumericAttributes: float
        self.stdPairedTTestValueForNumericAttributes: float

        self.maxChiSquareValueForDiscreteAttributes: float
        self.minChiSquareValueForDiscreteAttributes: float
        self.avgChiSquareValueForDiscreteAttributes: float
        self.stdChiSquareValueForDiscreteAttributes: float

        self.maxChiSquareValueForDiscreteAndDiscreteAttributes: float
        self.minChiSquareValueForDiscreteAndDiscreteAttributes: float
        self.avgChiSquareValueForDiscreteAndDiscreteAttributes: float
        self.stdChiSquareValueForDiscreteAndDiscreteAttributes: float

        #
        self.discreteAttributesList: list
        self.numericAttributesList: list

        self.stcop = StatisticOperation()
    def getDatasetBasedFeature(self, datadict, classifier):
        '''
        获取数据集的基本特征
        :param datadict:
        :param classifier:
        :return:dict
        '''
        try:
            self.processGeneralDatasetInfo(datadict)

            self.processInitialEvaluationInformation(datadict, classifier)

            self.processEntropyBasedMeasures(datadict)

            self.processAttributesStatisticalTests(datadict)

        except Exception as ex:
            logger.Error(f'Failed in func "getDatasetBasedFeature" with exception: {ex}')
            #return None
        finally:
            return self.generateDatasetAttributesMap()

    def processGeneralDatasetInfo(self, datadict):
        '''
        提取基本信息
        :param datadict:
        :return:
        '''
        self.numOfInstances = len(datadict["data"])
        self.numOfFeatures = len(datadict["data"].columns)
        self.numOfNumericAttributes = 0
        self.numOfDiscreteAttributes = 0
        self.numericAttributesList = []
        self.discreteAttributesList = []

        for clin in datadict["Info"]:
            if clin.getType() == outputType.Numeric:
                self.numOfNumericAttributes += 1
                self.numericAttributesList.append(clin)

            elif clin.getType() == outputType.Discrete:
                self.numOfDiscreteAttributes += 1
                self.discreteAttributesList.append(clin)

        self.ratioOfNumericAttributes = self.numOfNumericAttributes / (
                self.numOfNumericAttributes + self.numOfDiscreteAttributes)
        self.ratioOfDiscreteAttributes = self.numOfDiscreteAttributes / (
                self.numOfNumericAttributes + self.numOfDiscreteAttributes)

        numOfValuesPerDiscreteAttribute = []
        for columnInfo in self.discreteAttributesList:
            numOfValuesPerDiscreteAttribute.append(columnInfo.getNumsOfUnique())

        if len(numOfValuesPerDiscreteAttribute) > 0:
            self.maxNumberOfDiscreteValuesPerAttribute = max(numOfValuesPerDiscreteAttribute)
            self.minNumberOfDiscreteValuesPerAttribute = min(numOfValuesPerDiscreteAttribute)
            self.avgNumOfDiscreteValuesPerAttribute = sum(numOfValuesPerDiscreteAttribute) / len(
                numOfValuesPerDiscreteAttribute)

            self.stdNumOfDiscreteValuesPerAttribute = np.asarray(numOfValuesPerDiscreteAttribute,
                                                                 dtype=np.float32).std()


        else:
            self.maxNumberOfDiscreteValuesPerAttribute = 0
            self.minNumberOfDiscreteValuesPerAttribute = 0
            self.avgNumOfDiscreteValuesPerAttribute = 0
            self.stdNumOfDiscreteValuesPerAttribute = 0

    def processInitialEvaluationInformation(self, datadict, classifier: str):
        '''
        用于在初始数据字典上获取有关分类器性能的信息。对于培训数据集，需要提供整个datadict。对于测试数据集，只有训练数据集。
        :param datadict:
        :param classifier:
        :return:
        '''
        wrapperEvaluator = None
        wrapperName = 'AucWrapperEvaluator'
        if wrapperName == 'AucWrapperEvaluator':
            wrapperEvaluator = AucWrapperEvaluation()
        else:
            logger.Error('Wrapper Error')

        classificationResult = wrapperEvaluator.ProduceClassifications(datadict, classifier)

        self.aucValues = classificationResult.getAuc()
        self.logLossValues = classificationResult.getLogLoss()
        self.FMeasureValues = classificationResult.getFMeasureValues()

    def processEntropyBasedMeasures(self, datadict):
        '''
        计算交叉熵
        :param datadict:
        :return:
        '''
        IGScoresPerColumnIndex = []
        IGScoresPerDiscreteColumnIndex = []
        IGScoresPerNumericColumnIndex = []

        ige = InformationGainFilterEvaluator()
        data = datadict["data"]
        for idx in data.columns:
            ci = data[idx]

            if ci.dtype != "float64" and ci.dtype != "float32" and ci.dtype != "int64" and ci.dtype != "int32":
                continue

            indicedList = []
            indicedList.append(idx)
            # 此处留坑
            replicatedDataset = copy.deepcopy(datadict)
            column = None
            for cl in replicatedDataset["Info"]:
                if cl.getName() == ci.name:
                    column = cl
                    break
            if column is None:
                logger.Error(ci.name, "columninfo is not exist")
            newcolumn = [ci.name, ci, column]
            tempList = []
            tempList.append(newcolumn)
            ige.initFEvaluation(tempList)
            score = ige.produceScore(replicatedDataset, None, None, None)
            IGScoresPerColumnIndex.append(score)

            if ci.dtype == "int64" or ci.dtype == "int32":
                IGScoresPerDiscreteColumnIndex.append(score)
            else:
                IGScoresPerNumericColumnIndex.append(score)

        IGScoresPerDiscreteColumnIndex = np.array(IGScoresPerDiscreteColumnIndex)
        IGScoresPerNumericColumnIndex = np.array(IGScoresPerNumericColumnIndex)
        IGScoresPerColumnIndex = np.array(IGScoresPerColumnIndex)
        self.maxIGVal = np.max(IGScoresPerColumnIndex)
        self.minIGVal = np.min(IGScoresPerColumnIndex)
        self.avgIGVal = np.mean(IGScoresPerColumnIndex)
        self.stdIGVal = np.std(IGScoresPerColumnIndex)

        if IGScoresPerDiscreteColumnIndex.shape[0] > 0:
            self.discreteAttsMaxIGVal = np.max(IGScoresPerDiscreteColumnIndex)
            self.discreteAttsMinIGVal = np.min(IGScoresPerDiscreteColumnIndex)
            self.discreteAttsAvgIGVal = np.mean(IGScoresPerDiscreteColumnIndex)
            self.discreteAttsStdIGVal = np.std(IGScoresPerDiscreteColumnIndex)
        else:
            self.discreteAttsMaxIGVal = 0
            self.discreteAttsMinIGVal = 0
            self.discreteAttsAvgIGVal = 0
            self.discreteAttsStdIGVal = 0

        if IGScoresPerNumericColumnIndex.shape[0] > 0:
            self.numericAttsMaxIGVal = np.max(IGScoresPerNumericColumnIndex)
            self.numericAttsMinIGVal = np.min(IGScoresPerNumericColumnIndex)
            self.numericAttsAvgIGVal = np.mean(IGScoresPerNumericColumnIndex)
            self.numericAttsStdIGVal = np.std(IGScoresPerNumericColumnIndex)
        else:
            self.numericAttsMaxIGVal = 0
            self.numericAttsMinIGVal = 0
            self.numericAttsAvgIGVal = 0
            self.numericAttsStdIGVal = 0

    def processAttributesStatisticalTests(self, datadict):
        '''
        用于计算数据集中不同属性的相关性。对于数值属性，我们在每一对之间进行配对T检验。对于离散属性，我们进行卡方检验。最后，我们将数值属性离散化，并对所有属性进行额外的Chi-Suqare测试。
        :param datadict:
        :return:
        '''
        pairedTTestValuesList = []
        for i in range(len(self.numericAttributesList) - 1):
            for j in range(i + 1, len(self.numericAttributesList)):
                if i != j:
                    tstat, pval = scipy.stats.ttest_ind(
                        datadict['data'][self.numericAttributesList[i].getName()].values.compute(),
                        datadict['data'][self.numericAttributesList[j].getName()].values.compute())
                    tTestVal = abs(tstat)
                    if not np.isnan(tTestVal) and not np.isinf(tTestVal):
                        pairedTTestValuesList.append(tTestVal)

        if len(pairedTTestValuesList) > 0:
            self.maxPairedTTestValueForNumericAttributes = max(pairedTTestValuesList)
            self.minPairedTTestValueForNumericAttributes = min(pairedTTestValuesList)
            self.avgPairedTTestValueForNumericAttributes = np.average(pairedTTestValuesList)
            self.stdPairedTTestValueForNumericAttributes = np.std(pairedTTestValuesList)

        else:
            self.maxPairedTTestValueForNumericAttributes = 0
            self.minPairedTTestValueForNumericAttributes = 0
            self.avgPairedTTestValueForNumericAttributes = 0
            self.stdPairedTTestValueForNumericAttributes = 0

        chiSquaredTestValuesList = []
        for i in range(len(self.discreteAttributesList) - 1):
            for j in range(i + 1, len(self.discreteAttributesList)):
                if i != j:

                    counts = self.generateDiscreteAttributesCategoryIntersection(datadict['data'], self.discreteAttributesList[i], self.discreteAttributesList[j])
                    if counts is None:
                        continue
                    testVal = self.stcop.chisquare(counts)
                    if not np.isnan(testVal) and not np.isinf(testVal):
                        chiSquaredTestValuesList.append(testVal)

        if len(chiSquaredTestValuesList) > 0:
            self.maxChiSquareValueForDiscreteAttributes = max(chiSquaredTestValuesList)
            self.minChiSquareValueForDiscreteAttributes = min(chiSquaredTestValuesList)
            self.avgChiSquareValueForDiscreteAttributes = np.average(chiSquaredTestValuesList)
            self.stdChiSquareValueForDiscreteAttributes = np.std(chiSquaredTestValuesList)

        else:
            self.maxChiSquareValueForDiscreteAttributes = 0
            self.minChiSquareValueForDiscreteAttributes = 0
            self.avgChiSquareValueForDiscreteAttributes = 0
            self.stdChiSquareValueForDiscreteAttributes = 0

        # 最后，我们将数字特征离散化，并进行额外的卡方评估
        bins = theproperty.DiscretizerBinsNumber
        discretizedColumns = []
        for ci in self.numericAttributesList:
            erduo = Discretizer(bins)
            tempColumnsList = []
            tempColumnsList.append(ci)
            sourceColumnslist = [{'name': tl.getName(), 'type': tl.getType()} for tl in tempColumnsList]
            erduo.processTrainingSet(datadict['data'], sourceColumnslist, None)
            discretizedAttribute = erduo.generateColumn(datadict['data'], sourceColumnslist, None)
            discretizedAttdata = list(discretizedAttribute['data'].compute().values)

            discretizedColumns.append(discretizedAttdata)

        # 现在，我们将所有原始离散属性添加到此列表中，并再次运行卡方检验
        discretizedColumns += self.discreteAttributesList
        chiSquaredTestValuesList = []
        for i in range(len(discretizedColumns) - 1):
            for j in range(i + 1, len(discretizedColumns)):
                if (i != j):
                    counts = self.generateDiscreteAttributesCategoryIntersection(datadict['data'], discretizedColumns[i], discretizedColumns[j])
                    if counts is None:
                        continue
                    testVal = self.stcop.chisquare(counts)
                    if not np.isnan(testVal) and not np.isinf(testVal):
                        chiSquaredTestValuesList.append(testVal)

        if len(chiSquaredTestValuesList) > 0:
            self.maxChiSquareValueForDiscreteAndDiscreteAttributes = max(chiSquaredTestValuesList)
            self.minChiSquareValueForDiscreteAndDiscreteAttributes = min(chiSquaredTestValuesList)
            self.avgChiSquareValueForDiscreteAndDiscreteAttributes = np.average(chiSquaredTestValuesList)
            self.stdChiSquareValueForDiscreteAndDiscreteAttributes = np.std(chiSquaredTestValuesList)
           

        else:
            self.maxChiSquareValueForDiscreteAndDiscreteAttributes = 0
            self.minChiSquareValueForDiscreteAndDiscreteAttributes = 0
            self.avgChiSquareValueForDiscreteAndDiscreteAttributes = 0
            self.stdChiSquareValueForDiscreteAndDiscreteAttributes = 0


    def generateDatasetAttributesMap(self):
        '''
        生成字典
        :return: dict
        '''
        attributes = {}

        attributes[len(attributes)] = AttributeInfo("numOfInstances", outputType.Numeric, self.numOfInstances, -1)
        attributes[len(attributes)] = AttributeInfo("maxPairedTTestValueForNumericAttributes", outputType.Numeric,
                              self.maxPairedTTestValueForNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("numOfFeatures", outputType.Numeric, self.numOfFeatures, -1)
        attributes[len(attributes)] = AttributeInfo("numOfNumericAttributes", outputType.Numeric, self.numOfNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("numOfDiscreteAttributes", outputType.Numeric, self.numOfDiscreteAttributes, -1)


        attributes[len(attributes)] = AttributeInfo("ratioOfNumericAttributes", outputType.Numeric, self.ratioOfNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("ratioOfDiscreteAttributes", outputType.Numeric, self.ratioOfDiscreteAttributes,-1)
        attributes[len(attributes)] = AttributeInfo("maxNumberOfDiscreteValuesPerAttribute", outputType.Numeric,
                             self.maxNumberOfDiscreteValuesPerAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("minNumberOfDiscreteValuesPerAttribute", outputType.Numeric,
                             self.minNumberOfDiscreteValuesPerAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("avgNumOfDiscreteValuesPerAttribute", outputType.Numeric,
                              self.avgNumOfDiscreteValuesPerAttribute, -1)


        attributes[len(attributes)] = AttributeInfo("minPairedTTestValueForNumericAttributes", outputType.Numeric,
                              self.minPairedTTestValueForNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("avgPairedTTestValueForNumericAttributes", outputType.Numeric,
                              self.avgPairedTTestValueForNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("stdPairedTTestValueForNumericAttributes", outputType.Numeric,
                              self.stdPairedTTestValueForNumericAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("maxChiSquareValueForDiscreteAttributes", outputType.Numeric,
                              self.maxChiSquareValueForDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("minChiSquareValueForDiscreteAttributes", outputType.Numeric,
                              self.minChiSquareValueForDiscreteAttributes, -1)


        attributes[len(attributes)] = AttributeInfo("avgChiSquareValueForDiscreteAttributes", outputType.Numeric,
                              self.avgChiSquareValueForDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("stdChiSquareValueForDiscreteAttributes", outputType.Numeric,
                              self.stdChiSquareValueForDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("aucValues", outputType.Numeric, self.aucValues, -1)
        attributes[len(attributes)] = AttributeInfo("maxChiSquareValueForDiscreteAndDiscreteAttributes", outputType.Numeric,
                              self.maxChiSquareValueForDiscreteAndDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("logLossValues", outputType.Numeric, self.logLossValues, -1)


        attributes[len(attributes)] = AttributeInfo("maxIGVal", outputType.Numeric, self.maxIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("minIGVal", outputType.Numeric, self.minIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("avgIGVal", outputType.Numeric, self.avgIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("stdIGVal", outputType.Numeric, self.stdIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("discreteAttsMaxIGVal", outputType.Numeric, self.discreteAttsMaxIGVal, -1)


        attributes[len(attributes)] = AttributeInfo("discreteAttsMinIGVal", outputType.Numeric, self.discreteAttsMinIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("discreteAttsAvgIGVal", outputType.Numeric, self.discreteAttsAvgIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("discreteAttsStdIGVal", outputType.Numeric, self.discreteAttsStdIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("numericAttsMaxIGVal", outputType.Numeric, self.numericAttsMaxIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("numericAttsMinIGVal", outputType.Numeric, self.numericAttsMinIGVal, -1)


        attributes[len(attributes)] = AttributeInfo("numericAttsAvgIGVal", outputType.Numeric, self.numericAttsAvgIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("numericAttsStdIGVal", outputType.Numeric, self.numericAttsStdIGVal, -1)
        attributes[len(attributes)] = AttributeInfo("minChiSquareValueForDiscreteAndDiscreteAttributes", outputType.Numeric,
                              self.minChiSquareValueForDiscreteAndDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("avgChiSquareValueForDiscreteAndDiscreteAttributes", outputType.Numeric,
                              self.avgChiSquareValueForDiscreteAndDiscreteAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("stdChiSquareValueForDiscreteAndDiscreteAttributes", outputType.Numeric,
                              self.stdChiSquareValueForDiscreteAndDiscreteAttributes, -1)
        

        attributes[len(attributes)] = AttributeInfo("FMeasureValues", outputType.Numeric,
                                            self.FMeasureValues, -1)

        return attributes

    def generateDiscreteAttributesCategoryIntersection(self, data, col1, col2, n: int = theproperty.DiscretizerBinsNumber, m: int = theproperty.DiscretizerBinsNumber):
        newcol1 = col1
        newcol2 = col2
        if type(col1) != list:
            n = col1.getNumsOfUnique()
            newcol1 = data[col1.getName()].compute().values
        if type(col2) != list:
            m = col2.getNumsOfUnique()
            newcol2 = data[col2.getName()].compute().values
        if len(newcol1) != len(newcol2):
            return None

        list1 = np.zeros((n, m), "int32")
        for i in range(0, len(newcol1)):
            list1[newcol1[i]][newcol2[i]] += 1
        return list1

