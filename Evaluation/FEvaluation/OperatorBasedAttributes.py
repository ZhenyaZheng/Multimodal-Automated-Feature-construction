import os
import pandas as pd
import numpy as np
import dask.dataframe as dd
from scipy import stats

from Evaluation.FEvaluation.AttributeInfo import AttributeInfo
from Evaluation.FEvaluation.InformationGain import InformationGainFilterEvaluator
from Evaluation.FEvaluation.StatisticOperation import StatisticOperation
from MAFC_Operator import Operators
from logger.logger import logger
from MAFC_Operator.operator_base import outputType, operatorType


class OperatorBasedAttributes:
    def __init__(self):
        self.statisticoperation = StatisticOperation()

    def getOperatorsBasedAttributes(self, datadict, oa, evaluationatt):
        '''
        为所生成属性的“父级”生成元特征，这些元特征不需要计算要计算的生成属性的值
        :param datadict: 
        :param oa: 
        :return: 
        '''
        try:
            datadictReplica = datadict.replicateDataset()
            #留坑
            datadictReplica.addColumn(evaluationatt)
            tempList = []
            tempList.append(evaluationatt)
            igfe = InformationGainFilterEvaluator()
            igfe.initFEvaluation(tempList)
            self.IGScore = igfe.produceScore(datadictReplica, None, None, None)

            self.ProcessOperators(oa)

            self.processSourceAndTargetAttributes(datadict["data"], oa)

            self.performStatisticalTestsOnSourceAndTargetAttributes(datadict['data'], oa)

            #self.performStatisticalTestOnOperatorAssignmentAndDatasetAtributes(datadict['data'], oa)

            return self.generateInstanceAttributesMap()
        except Exception as ex:
            logger.Error(f'Failed in func "getOperatorsBasedAttributes" with exception: {ex}')
            return None

    def ProcessOperators(self, oa: Operators):
        '''
        分析Operators对象的特征——构成该对象的特征。这里不处理分析的属性本身。
        :param datadict:
        :param oa:
        :return:
        '''
        if oa.sourceColumns != None:
            self.numsOfSources = len(oa.sourceColumns)
        else:
            self.numsOfSources = 0

        self.numOfNumericSources = 0
        self.numOfDiscreteSources = 0
        self.numOfDateSources = 0
        if oa.sourceColumns != None:
            for ci in oa.sourceColumns:
                if ci['type'] == outputType.Numeric:
                    self.numOfNumericSources += 1
                elif ci['type'] == outputType.Discrete:
                    self.numOfDiscreteSources += 1
                elif ci['type'] == outputType.Date:
                    self.numOfDateSources += 1
        self.operatorTypeIdentifier = self.getOperatorTypeID(oa.getOperator().getType())
        self.isOutputDiscrete = 0
        if oa.secondoperators != None:
            if oa.secondoperators.getOutputType() == outputType.Discrete:
                self.isOutputDiscrete = 1
        else:
            if oa.getOperator().getOutputType() == outputType.Discrete:
                self.isOutputDiscrete = 1
        self.discreteInuse = self.getDiscreteID(oa.secondoperators)
        self.normalizerInUse = self.getNormalizerID(oa.secondoperators)
        self.numOfDiscreteValues = self.getNumOfNewAttributeDiscreteValues(oa)

    def getOperatorTypeID(self, type):
        if type == operatorType.Unary:
            return 1
        elif type == operatorType.Binary:
            return 2
        elif type == operatorType.GroupBy:
            return 3
        elif type == operatorType.TimeGroupBy:
            return 4
        else:
            logger.Error("operatorType Error")

    def getDiscreteID(self,oper):
        if oper == None:
            return 0

        namedict = {"Discretizer":1,"DayofWeek":2,"HourofDay":3,"IsWeekend":4}
        if namedict.get(oper.getName()) != None:
            return namedict.get(oper.getName())
        return 0

    def getNormalizerID(self,oper):
        if oper == None:
            return 0
        if oper.getName() == "StdOperator":
            return 1
        return 0

    def getNumOfNewAttributeDiscreteValues(self,oa):
        if oa.secondoperators != None:
            return oa.secondoperators.getNumOfBins()
        else:
            if oa.getOperator().getOutputType() != outputType.Discrete:
                return -1
            else :
                return oa.getOperator().getNumOfBins()

    def processSourceAndTargetAttributes(self,dataset: dd, oa : Operators):
        '''

        :param oa:
        :return:
        '''
        sourceattributelist = []
        for sourceatts in oa.sourceColumns:
            if sourceatts.getType() == outputType.Discrete:
                sourceattributelist.append(sourceatts.getNumsOfUnique())

        self.maxNumOfDiscreteSourceAttribtueValues = 0
        self.minNumOfDiscreteSourceAttribtueValues = 0
        self.avgNumOfDiscreteSourceAttribtueValues = 0
        self.stdNumOfDiscreteSourceAttribtueValues = 0
        if len(sourceattributelist) != 0:
            self.maxNumOfDiscreteSourceAttribtueValues = np.max(sourceattributelist)
            self.minNumOfDiscreteSourceAttribtueValues = np.min(sourceattributelist)
            self.avgNumOfDiscreteSourceAttribtueValues = np.mean(sourceattributelist)
            self.stdNumOfDiscreteSourceAttribtueValues = np.std(sourceattributelist)

        self.maxValueOfNumericTargetAttribute = 0
        self.minValueOfNumericTargetAttribute = 0
        self.avgValueOfNumericTargetAttribute = 0
        self.stdValueOfNumericTargetAttribute = 0

        if oa.targetColumns == None or oa.targetColumns[0].getType() != outputType.Numeric:
            pass
        else:
            columnname = oa.targetColumns[0].getName()
            self.maxValueOfNumericTargetAttribute = dataset[columnname].max().compute()
            self.minValueOfNumericTargetAttribute = dataset[columnname].min().compute()
            self.avgValueOfNumericTargetAttribute = dataset[columnname].mean().compute()
            self.stdValueOfNumericTargetAttribute = dataset[columnname].std().compute()

    def performStatisticalTestsOnSourceAndTargetAttributes(self, dataset, oa: Operators):
        '''
        离散源特征的卡方分布
        :param dataset:
        :param oa:
        :return:
        '''
        self.chiSquareTestValueForSourceAttributes = 0
        if len(oa.sourceColumns) == 2:
            if oa.sourceColumns[0].getType() == outputType.Discrete and oa.sourceColumns[1].getType == outputType.Discrete:
                templist1 = list(dataset[oa.sourceColumns[0].getName()].values.compute())
                templist2 = list(dataset[oa.sourceColumns[1].getName()].values.compute())
                list1 = self.statisticoperation.generateDiscreteAttributesCategoryIntersection(templist1, templist2, oa.sourceColumns[0].getNumsOfUnique(), oa.sourceColumns[1].getNumsOfUnique())
                tempval = self.statisticoperation.chisquare(list1)
                if tempval != None:
                    self.chiSquareTestValueForSourceAttributes = tempval
                else:
                    self.chiSquareTestValueForSourceAttributes = -1
        self.pairedTTestValueForSourceAndTargetAttirbutes = 0
        if len(oa.sourceColumns) == 1 and oa.sourceColumns[0].getType() == outputType.Numeric and oa.targetColumns != None and len(oa.targetColumns) == 1:
            templist1 = list(dataset[oa.sourceColumns[0].getName()].values.compute())
            templist2 = list(dataset[oa.targetColumns[0].getName()].values.compute())
            self.pairedTTestValueForSourceAndTargetAttirbutes = stats.ttest_rel(templist1,templist2)

        self.maxChiSquareTsetForSourceAndTargetAttributes = 0
        self.minChiSquareTsetForSourceAndTargetAttributes = 0
        self.avgChiSquareTsetForSourceAndTargetAttributes = 0
        self.stdChiSquareTsetForSourceAndTargetAttributes = 0

        if len(oa.sourceColumns) == 1 and oa.targetColumns == None:
            pass
        else:
            columnstoanalyze = []
            for ci in oa.sourceColumns:
                if ci.getType() == outputType.Discrete:
                    columnstoanalyze.append(ci)
                else:
                    if ci.getType() == outputType.Numeric:
                        newcolumn, thedata = self.statisticoperation.discretizeNumericColumn(dataset, ci, None)
                        columnstoanalyze.append(newcolumn)
                        if newcolumn.getName() not in dataset.columns:
                            dataset = dataset.merge(pd.DataFrame(data = newcolumn.getName(),columns=[thedata]))
            if len(columnstoanalyze) > 1:
                chiSquareTestValues = []
                for i in range(0 , len(columnstoanalyze) - 1):
                    for j in (i+1 , len(columnstoanalyze)):
                        templist1 = list(dataset[columnstoanalyze[i].getName()].values.compute())
                        templist2 = list(dataset[columnstoanalyze[j].getName()].values.compute())
                        list1 = self.statisticoperation.generateDiscreteAttributesCategoryIntersection(templist1,templist2,columnstoanalyze[i].getNumsOfUnique(),columnstoanalyze[j].getNumsOfUnique())
                        chiSquareTestVal = self.statisticoperation.chisquare(list1)
                        if chiSquareTestVal != None:
                            chiSquareTestValues.append(chiSquareTestVal)
                    if len(chiSquareTestValues) > 0:
                        self.maxChiSquareTsetForSourceAndTargetAttributes = np.max(chiSquareTestValues)
                        self.minChiSquareTsetForSourceAndTargetAttributes = np.min(chiSquareTestValues)
                        self.avgChiSquareTsetForSourceAndTargetAttributes = np.mean(chiSquareTestValues)
                        self.stdChiSquareTsetForSourceAndTargetAttributes = np.std(chiSquareTestValues)

    def generateInstanceAttributesMap(self):
        attributes = {}
        attributes[len(attributes)] = AttributeInfo("numsOfSources", outputType.Numeric,
                                                    self.numsOfSources, -1)
        attributes[len(attributes)] = AttributeInfo("numOfNumericSources", outputType.Numeric,
                                                    self.numOfNumericSources, -1)
        attributes[len(attributes)] = AttributeInfo("numOfDiscreteSources", outputType.Numeric,
                                                    self.numOfDiscreteSources, -1)
        attributes[len(attributes)] = AttributeInfo("numOfDateSources", outputType.Numeric,
                                                    self.numOfDateSources, -1)
        attributes[len(attributes)] = AttributeInfo("isOutputDiscrete", outputType.Discrete,
                                                    self.isOutputDiscrete, 2)
        attributes[len(attributes)] = AttributeInfo("operatorTypeIdentifier", outputType.Discrete,
                                                    self.operatorTypeIdentifier, 4)

        attributes[len(attributes)] = AttributeInfo("discreteInuse", outputType.Discrete,
                                                    self.discreteInuse, 2)
        attributes[len(attributes)] = AttributeInfo("normalizerInUse", outputType.Discrete,
                                                    self.normalizerInUse, 2)
        attributes[len(attributes)] = AttributeInfo("numOfDiscreteValues", outputType.Numeric,
                                                    self.numOfDiscreteValues, -1)
        attributes[len(attributes)] = AttributeInfo("IGScore", outputType.Numeric,
                                                    self.IGScore, -1)
        attributes[len(attributes)] = AttributeInfo("maxNumOfDiscreteSourceAttribtueValues",
                                                    outputType.Numeric,
                                                    self.maxNumOfDiscreteSourceAttribtueValues, -1)
        attributes[len(attributes)] = AttributeInfo("minNumOfDiscreteSourceAttribtueValues",
                                                    outputType.Numeric,
                                                    self.minNumOfDiscreteSourceAttribtueValues, -1)
        attributes[len(attributes)] = AttributeInfo("avgNumOfDiscreteSourceAttribtueValues",
                                                    outputType.Numeric,
                                                    self.avgNumOfDiscreteSourceAttribtueValues, -1)
        attributes[len(attributes)] = AttributeInfo("stdNumOfDiscreteSourceAttribtueValues",
                                                    outputType.Numeric,
                                                    self.stdNumOfDiscreteSourceAttribtueValues, -1)
        attributes[len(attributes)] = AttributeInfo("maxValueOfNumericTargetAttribute",
                                                    outputType.Numeric,
                                                    self.maxValueOfNumericTargetAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("minValueOfNumericTargetAttribute",
                                                    outputType.Numeric,
                                                    self.minValueOfNumericTargetAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("avgValueOfNumericTargetAttribute",
                                                    outputType.Numeric,
                                                    self.avgValueOfNumericTargetAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("stdValueOfNumericTargetAttribute",
                                                    outputType.Numeric,
                                                    self.stdValueOfNumericTargetAttribute, -1)
        attributes[len(attributes)] = AttributeInfo("chiSquareTestValueForSourceAttributes",
                                                    outputType.Numeric,
                                                    self.chiSquareTestValueForSourceAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("pairedTTestValueForSourceAndTargetAttirbutes",
                                                    outputType.Numeric,
                                                    self.pairedTTestValueForSourceAndTargetAttirbutes, -1)
        attributes[len(attributes)] = AttributeInfo("maxChiSquareTsetForSourceAndTargetAttributes",
                                                    outputType.Numeric,
                                                    self.maxChiSquareTsetForSourceAndTargetAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("minChiSquareTsetForSourceAndTargetAttributes",
                                                    outputType.Numeric,
                                                    self.minChiSquareTsetForSourceAndTargetAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("avgChiSquareTsetForSourceAndTargetAttributes",
                                                    outputType.Numeric,
                                                    self.avgChiSquareTsetForSourceAndTargetAttributes, -1)
        attributes[len(attributes)] = AttributeInfo("stdChiSquareTsetForSourceAndTargetAttributes",
                                                    outputType.Numeric,
                                                    self.stdChiSquareTsetForSourceAndTargetAttributes, -1)


        return attributes

