from text.TextOperator import TextOperator
from spacy.lang.en import English

class CountCharacter(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getCountChara(data, nlp):
            nums = 0
            words = nlp(data)
            for word in words:
                nums += len(word)
            return nums
        series = data.iloc[:, -1].apply(getCountChara, nlp=nlp, meta=('getCountChara', 'i8'))
        return series

    def getName(self):
        return "CountCharacter"
