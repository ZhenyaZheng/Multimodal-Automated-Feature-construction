from spacy.lang.en import English
from text.TextOperator import TextOperator


class IsVerbaferNoun(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getIsVerbaferNoun(data, nlp):
            doc = nlp(data)
            nums = 0
            pos_tags = [token.pos_ for token in doc]
            for index, pos in enumerate(pos_tags):
                # Check if the current token is a proper noun
                if pos == 'PROPN':
                    # Check if the next token is a verb
                    if pos_tags[index + 1] == 'VERB':
                        nums += 1
                        break
                return nums
        series = data.iloc[:, -1].apply(getIsVerbaferNoun, nlp=nlp, meta=('getIsVerbaferNoun', 'i8'))
        return series

    def getName(self):
        return "IsVerbaferNoun"
