import pandas as pd
import dask.dataframe as dd
from text.TextOperator import TextOperator
from text.lexicon import lexicons_features_vectors
from text.stanford_nlp import StanfordNLP


class PolarityofNegative(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        def pol(resvec):
            res = resvec[4]
            if res >= -2:
                return 0
            else:
                return 1

        datalist = list(data.iloc[:, -1].compute().values)

        nlp_helper = StanfordNLP()
        words = []
        pos_tags = []
        for text in datalist:
            word, pos_tag = nlp_helper.pos_tag(text)
            words.append(word)
            pos_tags.append(pos_tag)
        wordvec = lexicons_features_vectors(words, pos_tags)
        newseries = [pol(i) for i in wordvec]
        theseries = pd.Series(newseries, name=self.getName(), dtype="int32")
        series = dd.from_pandas(theseries, npartitions=1).reset_index().iloc[:, -1]
        return series

    def getName(self):
        return "PolarityofNegative"
