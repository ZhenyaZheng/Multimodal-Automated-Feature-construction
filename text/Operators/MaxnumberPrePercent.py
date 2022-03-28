from text.TextOperator import TextOperator
from spacy.lang.en import English


class MaxNumberPrePercent(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getMaxPercent(data, nlp):
            doc = nlp(data)
            maxnums = 0
            for token in doc:
                if token.like_num:
                    if token.i == len(doc) - 1:
                        continue
                    # Get the next token in the document
                    next_token = doc[token.i + 1]
                    # Check if the next token's text equals '$'
                    if next_token.text == '$':
                        num = (int)(token.text)
                        if num > maxnums:
                            maxnums = num
            return maxnums
        series = data.iloc[:, -1].apply(getMaxPercent, nlp=nlp, meta=('getMaxPercent', 'f8'))
        return series

    def getName(self):
        return "MaxNumberPrePercent"
