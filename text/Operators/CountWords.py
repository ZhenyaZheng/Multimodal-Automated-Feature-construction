from text.TextOperator import TextOperator
from spacy.lang.en import English

class CountWords(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getCountWords(data, nlp):
            words = nlp(data)
            return len(words)
        series = data.iloc[:, -1].apply(getCountWords, nlp=nlp, meta=('getCountWords', 'i8'))
        return series

    def getName(self):
        return "CountWords"
