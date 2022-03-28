import dask.dataframe as dd
from text.TextOperator import TextOperator
from text.cluster import processCluster
import pandas as pd
class ClusterofSentence(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        datalist = list(data.iloc[:, -1].compute().values)
        newseries = processCluster(datalist)
        theseries = pd.Series(newseries, name=self.getName(), dtype="int32")
        series = dd.from_pandas(theseries, npartitions=1).reset_index().iloc[:, -1]
        return series

    def getName(self):
        return "ClusterofSentence"
