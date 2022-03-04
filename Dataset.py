import cv2
import dask.dataframe as dd
import os
class Dataset:
    def __init__(self,data_path = None):
        '''
        :param data_path:数据集路径，是一个字典:{'image_path':"",'text_path':"",'tabular_path':""}
        '''
        self.data_path = data_path
        self.data_tabular = self.read_tabular()
        self.data_text = self.read_text()
        self.data_image = self.read_image()



    def read_text(self):
        '''
        :return:Dask.Dataframe
        '''
        text_path = self.data_path['text_path']
        if text_path is None:
            return None
        text_data = dd.read_csv(text_path)
        return text_data


    def read_image(self):
        '''
        :return:cv2
        '''
        image_path = self.data_path['image_path']
        if image_path is None:
            return None
        imgs = []
        for filename in os.listdir(image_path):
            img = cv2.imread(os.path.join(image_path,filename))
            imgs.append(img)
        return imgs

    def read_tabular(self):
        '''

        :return:Dask.Dataframe
        '''
        tabular_path = self.data_path['tabular_path']
        if tabular_path is None:
            return None
        tabular_data = dd.read_csv(tabular_path)
        return tabular_data

