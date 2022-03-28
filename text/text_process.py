import copy
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

def process(textdata, opertorslist = None, ingorelist = None):
    '''

    :param textdata:dask.dataframe
    :param opertorslist: [str]
    :param ingorelist: [str]
    :return: dask.dataframe
    '''
    copydata = copy.deepcopy(textdata)
    operslist : list[TextOperator] = getOperator(opertorslist, ingorelist)
    for oper in operslist:
        newseries = oper.process(copydata)
        print(oper.getName())
        #seriesdata = newseries.compute()
        if newseries is not None and len(newseries.value_counts().compute()) > 1:
            textdata[oper.getName()] = newseries

    return textdata