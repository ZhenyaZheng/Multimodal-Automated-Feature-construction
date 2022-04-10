import dask.dataframe as dd
import pandas as pd

from Dataset import Dataset
from utils import getDatadict

from FeatureConstruction import FC, getDatadict
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
if __name__ == "__main__":

    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/heart.csv"}
    dataset = Dataset(datapath, name="heart")
    datadict = getDatadict(dataset)
    mlam = MLAttributeManager()
    mlam.getDatasetInstances(datadict)

    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/trainless.csv"}
    dataset = Dataset(datapath, name="testdata")
    data = FC(dataset, isiteration=True, iternums=1)
    data.compute()
    print("End")

    '''
    df = pd.read_csv("data/datasets/dataset_candidatedata.csv")

    print(df.shape)
    print(df.columns)
    '''
