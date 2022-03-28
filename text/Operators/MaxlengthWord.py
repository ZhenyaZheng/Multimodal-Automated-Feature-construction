from text.TextOperator import TextOperator
from spacy.lang.en import English


class MaxlengthWord(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getMaxlengthWord(data, nlp):
            words = nlp(data)
            word = None
            for wd in words:
                if word == None:
                    word = wd
                    continue
                if len(wd) > len(word):
                    word = wd
            return word
        series = data.iloc[:, -1].apply(getMaxlengthWord, nlp=nlp, meta=('getMaxlengthWord', 'object'))
        return series

    def getName(self):
        return "MaxlengthWord"
