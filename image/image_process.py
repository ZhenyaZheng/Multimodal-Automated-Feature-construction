import copy

import pandas as pd

from image.ImageOperator import ImageOperator
from image.ImageOperators import *
from logger.logger import logger
import dask.dataframe as dd

def getOperatorList():
    return [c.__name__ for c in ImageOperator.__subclasses__()]

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

def process(imagedata, imageoper=None, imageigoper=None):
    '''

        :param imagedata:dask.dataframe
        :param imageoper: [str]
        :param imageigoper: [str]
        :return: dask.dataframe
        '''
    #pdata = pd.DataFrame()
    data = copy.deepcopy(imagedata)
    del data[data.iloc[:, -1].name]
    operslist: list[ImageOperator] = getOperator(imageoper, imageigoper)
    for oper in operslist:
        try:
            newseries = oper.process(imagedata)
            #print(oper.getName())

            if newseries is not None:
                #newseriesview = newseries.compute()
                if type(newseries) == dd.DataFrame:
                    data = data.merge(newseries, how="left")
                elif type(newseries) == dd.core.Series:
                    data[oper.getName()] = newseries
        except Exception as ex:
                logger.Error(f'Failed in func "image_process" with exception: {ex}')
    data = data.set_index("id")
    return data