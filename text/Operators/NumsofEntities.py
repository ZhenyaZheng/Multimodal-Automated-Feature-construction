import pandas as pd
import dask.dataframe as dd
from text.TextOperator import TextOperator
import spacy

class NumsofEntities(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = spacy.load('en_core_web_sm')
        datalist = list(data.iloc[:, -1].compute().values)
        docs = list(nlp.pipe(datalist))
        newseries = [len(doc.ents) for doc in docs]
        theseries = pd.Series(newseries, name=self.getName(), dtype="int32")
        series = dd.from_pandas(theseries, npartitions=1).reset_index().iloc[:, -1]
        return series

    def getName(self):
        return "NumsofEntities"
