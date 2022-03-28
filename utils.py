import pickle

from Evaluation.FEvaluation.InformationGain import InformationGainFilterEvaluator
from Evaluation.FEvaluation.MLFEvalution import MLFEvaluation
from Evaluation.WEvaluation.AucWrapperEvaluation import AucWrapperEvaluation
from MAFC_Operator.ColumnInfo import ColumnInfo
from MAFC_Operator.operator_base import outputType
from logger.logger import logger
from text.text_process import process as txprocess
from image.image_process import process as improcess
def Image_FC(image_data):
    '''

    :param image_data:
    :return: dask.Dataframe
    '''
    if image_data is None:
        return None
    return improcess(image_data)

def Text_FC(text_data):
    '''
    :param text_data:
    :return: dask.Dataframe
    '''
    if text_data is None:
        return None
    return txprocess(text_data)

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
                data[name].astype("float64")
                columninfo = ColumnInfo(None, None, None, name, False, outputType.Numeric)
            else :
                columninfo = ColumnInfo(None, None, None, name, False, outputType.Discrete, lensofvalues)
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

def getEvaluation(name, datadict):
    evaluation = None
    if name == "AucWrapperEvaluation":
        evaluation = AucWrapperEvaluation()
    elif name == "InformationGain":
        evaluation = InformationGainFilterEvaluator()
    elif name == "MLFEvaluation":
        evaluation = MLFEvaluation(datadict)
    else:
        logger.Error("No this Evaluation" + name)
    return evaluation

def serialize(filepath , obj):
    with open(filepath, "wb") as file:
        pickle.dump(obj, file)

def deserialize(filepath):
    with open(filepath, "rb") as file:
        obj = pickle.load(file)
        return obj