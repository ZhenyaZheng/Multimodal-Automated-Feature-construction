from text.TextOperator import TextOperator
from spacy.lang.en import English

class MaxlengthofSentence(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getMaxlength(data, nlp):
            words = nlp(data)
            lens = 0
            for wd in words:
                if len(wd) > lens:
                    lens = len(wd)
            return lens
        series = data.iloc[:, -1].apply(getMaxlength, nlp=nlp, meta=('getMaxlength', 'i8'))
        return series

    def getName(self):
        return "MaxlengthofSentence"
