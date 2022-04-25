import dask.dataframe as dd
import pandas as pd
from Dataset import Dataset
from utils import getDatadict
from properties.properties import theproperty
from FeatureConstruction import FC, getDatadict, getNowTimeStr
from Evaluation.FEvaluation.MLAttributeManager import MLAttributeManager
if __name__ == "__main__":
    '''
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/test.csv"}
    dataset = Dataset(datapath, name="test")
    datadict = getDatadict(dataset)
    mlam = MLAttributeManager()
    mlam.getDatasetInstances(datadict)
    '''
    '''
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/trainless.csv"}
    dataset = Dataset(datapath, name="testdata")
    data = FC(dataset, isiteration=True, iternums=1)
    if data is not None:
        data = data.compute()
    print("End")
    '''
    '''
    df = pd.read_csv("data/datasets/dataset_candidatedata.csv")

    print(df.shape)
    print(df.columns)
    '''
    # datasetpath = "C:/Users/ZCRF/Desktop/dataset/"
    # datapath = {"image_path": datasetpath + "image/", "text_path": datasetpath + "text/text.csv", "tabular_path": datasetpath + "tabular/data.csv"}
    # dataset = Dataset(datapath, name="alltestdata")
    '''
    from properties.properties import theproperty
    theproperty.datasetname = "alltest"
    data = FC(None, isiteration=True, iternums=1)
    if data is not None:
        data = data.compute()
    print("End")
    '''
    #测试pandas
    '''
    theproperty.dataframe = "pandas"
    print(getNowTimeStr())
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/train.csv"}
    dataset = Dataset(datapath, name="hearttrain")
    datadict = getDatadict(dataset)
    mlam = MLAttributeManager()
    mlam.getDatasetInstances(datadict)
    print(getNowTimeStr())
    print("End")
    '''
    '''
    theproperty.dataframe = "pandas"
    print(getNowTimeStr())
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/test.csv"}
    dataset = Dataset(datapath, name="hearttest")
    data = FC(dataset, True, 10)
    print(getNowTimeStr())
    print("End")
    '''
    '''
    theproperty.dataframe = "pandas"
    datasetpath = "D:/data/dataset/"
    datapath = {"image_path": datasetpath + "image/", "text_path": datasetpath + "text/text.csv", "tabular_path": datasetpath + "tabular/data.csv"}
    dataset = Dataset(datapath, name="Alldata")

    data = FC(dataset, isiteration=True, iternums=1)
    if data is not None and theproperty.dataframe == "dask":
        data = data.compute()
    print("End")
    '''
    theproperty.dataframe = "pandas"
    print(getNowTimeStr())
    datapath = {"image_path": None, "text_path": None, "tabular_path": "data/otherdatas/phpkIxskf.csv"}
    dataset = Dataset(datapath, name="phpklxskf")
    data = FC(dataset, isiteration=True, iternums=1)
    if data is not None and theproperty.dataframe == "dask":
        data = data.compute()
    print(getNowTimeStr())
    print("End")