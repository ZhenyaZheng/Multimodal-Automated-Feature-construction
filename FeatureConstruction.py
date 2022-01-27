
from Dataset import Dataset
import dask

def Image_FC(image_data):
    pass

def Text_FC(text_data):
    pass


def _FC_(data):
    pass

def FC(dataset):
    image_fc = Image_FC(dataset.data_image)
    text_fc = Text_FC(dataset.data_text)
    ##合并image、text和form
    data = dask.Dataframe()
    df = _FC_(data)
    return df