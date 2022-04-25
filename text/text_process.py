import copy
import dask.dataframe as dd
import pandas as pd
from properties.properties import theproperty
from text.Operators import *
from text.TextOperator import TextOperator
from logger.logger import logger

def getOperatorList():
    return [c.__name__ for c in TextOperator.__subclasses__()]

def getOperator(oplist, iglist):
    alloplist = getOperatorList()
    if oplist == None:
        oplist = alloplist
    else:
        for opt in oplist:
            if opt not in alloplist:
                logger.Error(opt + " is not define")
    if iglist != None:
        oplist = list(set(oplist) - set(iglist))
    return [eval(opt + "()") for opt in oplist]

def process(textdata, opertorslist=None, ingorelist=None):
    '''

    :param textdata:dask.dataframe
    :param opertorslist: [str]
    :param ingorelist: [str]
    :return: dask.dataframe
    '''
    pdata = pd.DataFrame()
    if theproperty.dataframe == "dask":
        data = dd.from_pandas(pdata, npartitions=10)
    elif theproperty.dataframe == "pandas":
        data = pdata
    operslist : list[TextOperator] = getOperator(opertorslist, ingorelist)
    for oper in operslist:
        try:
            newseries = oper.process(textdata)
            #print(oper.getName())
            #seriesdata = newseries.compute()
            if newseries is not None:
                if theproperty.dataframe == "dask":
                    uniqueval = len(newseries.value_counts().compute())
                elif theproperty.dataframe == "pandas":
                    uniqueval = len(newseries.value_counts())
                if uniqueval > 1:
                    data[oper.getName()] = newseries
        except Exception as ex:
                logger.Error(f'Failed in func "text_process" with exception: {ex}')

    return data