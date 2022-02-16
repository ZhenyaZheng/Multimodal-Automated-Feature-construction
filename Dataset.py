
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
        pass

    def read_image(self):
        '''

        :return:cv2
        '''
        pass

    def read_tabular(self):
        '''

        :return:Dask.Dataframe
        '''
        pass

    def __copy__(self):
        pass
