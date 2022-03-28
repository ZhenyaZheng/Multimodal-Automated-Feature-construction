import copy
import os.path
from shutil import copyfile

import numpy as np
import pandas as pd
from distributed import Client
from Evaluation.FEvaluation.OperatorBasedAttributes import OperatorBasedAttributes
import dask.dataframe
from Evaluation.FEvaluation.DatasetAttributes import DatasetAttributes
from Evaluation.FEvaluation.AttributeInfo import AttributeInfo
from properties.properties import theproperty
from MAFC_Operator.OperatorManager import OperatorManager
from Evaluation.WEvaluation.WEvaluation import WEvaluation
from utils import *
from dask_ml.wrappers import ParallelPostFit
from MAFC_Operator.operator_base import outputType


class MLAttributeManager:
    def __init__(self):
        pass

    def getBackgroundClassificationModel(self, datadict):
        backgroundFilePath = theproperty.backmodelpath + datadict["name"].name + "_model_classifier_obj"
        if os.path.isfile(backgroundFilePath):
            model = deserialize(backgroundFilePath)
            return model
        else:
            datasetfilepath = theproperty.datasetlocation
            if os.path.isdir(datasetfilepath):
                addhead = True
                for fp in os.listdir(datasetfilepath):
                    if os.path.isfile(datasetfilepath + fp) and datadict["name"] not in backgroundFilePath:
                        self.addFiletoTargetfile(backgroundFilePath, datasetfilepath + fp, addhead)
                        addhead = False
                    else:
                        logger.Info("skip file : " + fp)
            else:
                logger.Error("datasetlocation is not exist")
            if os.path.isfile(backgroundFilePath + ".csv"):
                datatrain = dask.dataframe.read_csv(backgroundFilePath + ".csv")
                y = datatrain.iloc[:, -1]
                del datatrain[y.name]
                model = self.buildModel(datatrain, y, theproperty.classifier)
                serialize(backgroundFilePath, model)
                return model
            else:
                logger.Error("modeldata is not exist")

    def buildModel(self, datatarin, target, classifier):
        wevaluation = WEvaluation()
        model = wevaluation.getClassifier(classifier)
        client = Client()
        clf = ParallelPostFit(model, scoring="r2")
        clf.fit(datatarin, target)
        client.close()
        return clf

    def addFiletoTargetfile(self, modelfilepath, datasetfilepath, addhead):
        modelfile = modelfilepath + ".csv"
        if os.path.isfile(modelfile) and not addhead:
            with open(modelfile, "a") as tarfile:
                with open(datasetfilepath, "r") as sourfile:
                    sourfile.readline()
                    a = sourfile.readline()
                    tarfile.writelines("\n")
                    while a != "":
                        print(a)
                        tarfile.writelines(a)
                        a = sourfile.readline()
        else:
            copyfile(datasetfilepath, modelfile)



    def getDatasetInstances(self, datadict):
        filename = datadict["data"].name + "_candidatedata.csv"
        filepath = theproperty.datasetlocation + filename
        if os.path.isfile(filepath):
            logger.Info(datadict["data"].name + "candidatedata has existed")
            datainstances = dask.dataframe.read_csv(filepath)
            return datainstances

        dataattsvalues = self.generateTrainsetAtts(datadict)
        datainstances = self.generateValuesTabular(dataattsvalues)
        pd.DataFrame.to_csv(datainstances, filepath)
        return datainstances

    def generateValuesTabularFromFE(self, candidateAttributes):
        tempattlist = [candidateAttributes]
        return self.getDatasetInstances(tempattlist)

    def generateTrainsetAtts(self, datadict):
        '''
        :param datadict:
        :return:[{}]
        '''
        candidateattslist = []
        classifiers = theproperty.classifiersforMLAttributes
        dbas = DatasetAttributes()
        evaluator = WEvaluation()
        for classifier in classifiers:
            evaluationresult = evaluator.runClassifier(classifier, datadict)
            originalAUC = evaluator.calculateAUC(evaluationresult)

            datasetatts = dbas.getDatasetBasedFeature(datadict, classifier)

            classifieratt = AttributeInfo("Classifier", outputType.Discrete, self.getClassifierIndex(classifier), 3)

            datasetatts[len(datasetatts)] = classifieratt

            oms = OperatorManager()
            unaryoperlist = theproperty.unaryoperator
            unaryoperators = oms.UnaryOperator(datadict, unaryoperlist)

            otheroperlist = theproperty.otheroperator
            otheroperators = oms.OtherOperator(datadict, otheroperlist)
            otheroperators += unaryoperators
            numofthread = theproperty.thread
            if numofthread > 1:
                pass
            else:
                for ops in otheroperators:
                    datacopy = copy.deepcopy(datadict)
                    candidateatt = [oms.generateColumn(datacopy["data"], ops, False)]
                    obas = OperatorBasedAttributes()
                    candidateattsdict = obas.getOperatorsBasedAttributes(datacopy, ops, candidateatt)
                    oms.addColumn(datacopy, candidateatt)
                    evaluationresult = evaluator.runClassifier(classifier, datacopy)
                    auc = evaluator.calculateAUC(evaluationresult)
                    deltaAUC = auc - originalAUC
                    if deltaAUC > 0.01:
                        classatt = AttributeInfo("classattribute", outputType.Discrete, 1, 2)
                        logger.Info("find positive match")
                    else:
                        classatt = AttributeInfo("classattribute", outputType.Discrete, 0, 2)

                    for datainfos in datasetatts.values():
                        candidateattsdict[len(candidateattsdict)] = datainfos
                    candidateattsdict[len(candidateattsdict)] = classatt
                    candidateattslist.append(candidateattsdict)
        return candidateattslist

    def generateValuesTabular(self, dataattsvalues):
        '''

        :param dataattsvalues: [{}]
        :return: pandas.dataframe
        '''
        attributes = self.generateAtts(dataattsvalues[0], len(dataattsvalues))
        df = pd.DataFrame(name = "MLtarindata")
        for atts in attributes:
            df.insert(len(df.columns), atts.name, atts)
        num = 0
        for dav in dataattsvalues:#{1:att,2:att}
            for ats in dav.items():#(1:att)
                index = ats[0]
                att = ats[1]
                df.iloc[:, index][num] = att.getValue()
            num += 1
        return df


    def generateAtts(self, dataattsvalue, sizen: int):
        '''

        :param dataattsvalue: dict
        :return:
        '''
        attributelist = []
        for attif in dataattsvalue.values():
            datase = np.zeros(sizen)
            if attif.getType() == outputType.Discrete:
                type = "int32"
            elif attif.getType() == outputType.Numeric:
                type = "float32"
            else:
                logger.Error("MLatt is not support except int and float type")
            att = pd.core.series.Series(datase, None, type, attif.getName())
            attributelist.append(att)

    def getClassifierIndex(self, classifiername: str):
        index = 0
        if classifiername == "RandomForest":
            index = 0
        elif classifiername == "DicisionTree":
            index = 1
        elif classifiername == "SVM":
            index = 2
        else:
            logger.Error("No this Model : " + classifiername)
        return index