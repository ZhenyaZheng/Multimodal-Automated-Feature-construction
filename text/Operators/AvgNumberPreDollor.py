from text.TextOperator import TextOperator
from spacy.lang.en import English


class AvgNumberPreDollor(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getAvgDollor(data, nlp):
            doc = nlp(data)
            sums = 0
            nums = 0
            for token in doc:
                if token.like_num:
                    if token.i == len(doc) - 1:
                        continue
                    # Get the next token in the document
                    next_token = doc[token.i + 1]
                    # Check if the next token's text equals '$'
                    if next_token.text == '$':
                        num = (int)(token.text)
                        sums += num
                        nums += 1
            if nums == 0:
                return 0
            else:
                return sums // nums
        series = data.iloc[:, -1].apply(getAvgDollor, nlp=nlp, meta=('getAvgDollor', 'f8'))
        return series

    def getName(self):
        return "AvgNumberPreDollor"