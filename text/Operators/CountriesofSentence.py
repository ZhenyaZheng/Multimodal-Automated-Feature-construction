from spacy.matcher import PhraseMatcher

from text.TextOperator import TextOperator
from spacy.lang.en import English

from text.country import Countries


class CountriesofSentence(TextOperator):
    def __init__(self):
        pass

    def process(self, data):
        '''

        :param data:dask.dataframe
        :return: dask.series
        '''
        nlp = English()
        def getCountries(data, nlp):
            doc = nlp(data)
            country_matcher = PhraseMatcher(nlp.vocab)
            countries = Countries()
            patterns = list(nlp.pipe(countries.getCountries()))
            country_matcher.add('COUNTRY', None, *patterns)
            # Call the matcher on the test document and print the result
            matches = country_matcher(doc)
            return len(matches)
        series = data.iloc[:, -1].apply(getCountries, nlp=nlp, meta=('getCountries', 'i8'))
        return series

    def getName(self):
        return "CountriesofSentence"
