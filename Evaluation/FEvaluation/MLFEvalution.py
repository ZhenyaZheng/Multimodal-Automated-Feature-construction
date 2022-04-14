import copy
from Evaluation.FEvaluation.FEvaluation import FEvaluation
from Evaluation.FEvaluation.AttributeInfo import AttributeInfo
from Evaluation.FEvaluation.OperatorBasedAttributes import OperatorBasedAttributes
from Evaluation.FEvaluation.DatasetAttributes import DatasetAttributes
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
from logger.logger import logger
from properties.properties import theproperty
from MAFC_Operator.operator_base import outputType
from MAFC_Operator.OperatorManager import OperatorManager
import dask.dataframe

class MLFEvaluation(FEvaluation):
    def __init__(self, datadict):
        super(MLFEvaluation, self).__init__()
        self.classifier = None
        self.evaluation = None
        self.datasetAttriutes = {}
        self.initBackModel(datadict)


    def initBackModel(self, datadict):
        logger.Info("Initializing Background Model for dataset " + datadict["data"].name)
        self.mla = MLAttributeManager()
        self.classifier = self.mla.getBackgroundClassificationModel(datadict)

        self.dba = DatasetAttributes()
        #self.datasetAttributes = self.dba.getDatasetBasedFeature(datadict, theproperty.classifier)

    def recalculateDatasetBasedFeatures(self, datadict):
        datadictcopy = copy.deepcopy(datadict)
        # index = 0
        # targetcolumn = datadictcopy["target"]
        #
        # while index < len(datadictcopy["Info"]):
        #     if datadictcopy["Info"][index].getName() == targetcolumn.name:
        #         break
        #     index += 1
        # if index != len(datadictcopy["Info"]):
        #     datadictcopy["Info"].pop(index)
        #del datadictcopy["data"][targetcolumn.name]
        self.datasetAttributes = self.dba.getDatasetBasedFeature(datadictcopy, theproperty.classifier)

    def setClassifier(self, classifier):
        self.classifier = classifier

    def setDataAttributes(self, datasetAttributes):
        self.datasetAttributes = datasetAttributes

    def setEvalution(self, evalution):
        self.evaluation = evalution

    def produceScore(self, datadict, currentScore, oa, candidateAttribute):
        try:
            if self.classifier is None:
                logger.Error("Classifier is not initialized")
            oba = OperatorBasedAttributes()
            #logger.Info("op.name = " + oa.getName())
            # listerror = ["{sources:[fc,];Targets:[mobile_wt,];GroupMin}", "{sources:[four_g,];Targets:[{sources:[battery_power,];Targets:[];StdOperator},];GroupMin}",
            #              "{sources:[wifi,];Targets:[m_dep,];GroupMin}","{sources:[mobile_wt,];Targets:[clock_speed,];AddOperator}",
            #              "{sources:[{sources:[px_height,];Targets:[];StdOperator},];Targets:[mobile_wt,];AddOperator}",
            #              "{sources:[dual_sim,];Targets:[clock_speed,];GroupMin}", "{sources:[{sources:[px_height,];Targets:[];StdOperator},];Targets:[battery_power,];AddOperator}",
            #              "{sources:[{sources:[clock_speed,];Targets:[];StdOperator},];Targets:[{sources:[battery_power,];Targets:[];StdOperator},];AddOperator}",
            #              "{sources:[{sources:[battery_power,];Targets:[];StdOperator},];Targets:[clock_speed,];DivisOperator}",
            #              "{sources:[sc_w,];Targets:[int_memory,];GroupMin}", "{sources:[pc,];Targets:[{sources:[battery_power,];Targets:[];StdOperator},];GroupMin}",
            #              "{sources:[{sources:[int_memory,];Targets:[];StdOperator},];Targets:[{sources:[px_width,];Targets:[];StdOperator},];DivisOperator}",
            #              "{sources:[n_cores,];Targets:[px_height,];GroupMin}"]
            # if oa.getName() in listerror:
            #     pass

            candidateAttributes = oba.getOperatorsBasedAttributes(datadict, oa, candidateAttribute)
            for das in self.datasetAttributes.values():
                candidateAttributes[len(candidateAttributes)] = das
            classifierattribute = AttributeInfo("Classifier", outputType.Discrete, 0, 2)
            candidateAttributes[len(candidateAttributes)] = classifierattribute

            df = self.mla.generateValuesTabularFromFE(candidateAttributes)
            model = self.classifier
            if df is None:
                return 0
            df = dask.dataframe.from_pandas(data=df, npartitions=1)
            # 预测
            df_true = model.predict_proba(df)
            #计算得分
            score = df_true.compute()[0][1]
            return score
        except Exception as ex:
            logger.Error(f"MLFEvaluation produceScore error: {ex}")
            return 0

    def needToRecalcScore(self) -> bool:
        return True

    def getEvalutionScoringMethod(self):
        return self.evaluationScoringMethod.ClassifierProbability

    def getClassifier(self):
        return self.classifier

    def getEvalution(self):
        return self.evaluation

