
class Dataset:
    def __init__(self,data_path = None):
        self.data_path = data_path
        self.data_tabular = self.read_tabular()
        self.data_text = self.read_text()
        self.data_image = self.read_image()



    def read_text(self):
        pass

    def read_image(self):
        pass

    def read_form(self):
        pass
