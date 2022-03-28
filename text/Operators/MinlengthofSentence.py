from text.TextOperator import TextOperator
from spacy.lang.en import English

class MinlengthofSentence(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getMinlength(data, nlp):
            words = nlp(data)
            lens = 1000000000
            for wd in words:
                if len(wd) < lens:
                    lens = len(wd)
            return lens
        series = data.iloc[:, -1].apply(getMinlength, nlp=nlp, meta=('getMinlength', 'i8'))
        return series

    def getName(self):
        return "MinlengthofSentence"
