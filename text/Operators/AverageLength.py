from text.TextOperator import TextOperator
from spacy.lang.en import English

class AverageLength(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getAvglength(data, nlp):
            nums = 0
            words = nlp(data)
            for word in words:
                nums += len(word)
            return nums // len(words)
        series = data.iloc[:, -1].apply(getAvglength, nlp=nlp, meta=('getAvglength', 'f8'))
        return series

    def getName(self):
        return "AverageLength"
