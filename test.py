'''
from Dataset import Dataset
from FeatureConstruction import FC, getDatadict
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
if __name__ == "__main__":
    datapath = {"image_path": None, "text_path": None, "tabular_path": "./data/nycflights/1990.csv"}
    dataset = Dataset(datapath)
    datadict = getDatadict(dataset)
    mlam = MLAttributeManager()
    mlam.getDatasetInstances(datadict)
'''
from text import *
import dask.dataframe as dd
textdata = dd.read_csv("data/text/test.csv")
#data = textdata.compute()
txprocess(textdata)
data = textdata.compute()
pass

