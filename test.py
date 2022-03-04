from Dataset import Dataset
from MAFC_Operator import *
from FeatureConstruction import FC
if __name__ == "__main__":
    datapath = {"image_path":None,"text_path":None,"tabular_path":"./data/nycflights/1990.csv"}
    dataset = Dataset(datapath)
    df = FC(dataset)
    print(df["Info"])
