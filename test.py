import dask.dataframe as dd
from Dataset import Dataset
from utils import getDatadict

from FeatureConstruction import FC, getDatadict
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
if __name__ == "__main__":
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/datasets/heart.csv"}
    dataset = Dataset(datapath)
    datadict = getDatadict(dataset)
    mlam = MLAttributeManager()
    mlam.getDatasetInstances(datadict)

'''
if __name__ == "__main__":
    datapath = {"image_path": "data/image/", "text_path": "data/text/yrr.csv", "tabular_path": "data/tabular/tabular.csv"}
    dataset = Dataset(datapath)
    datadict = getDatadict(dataset)
    data = datadict["data"].compute()
    print("END")
'''