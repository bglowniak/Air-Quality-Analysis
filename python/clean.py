import pandas as pd
import os.path
from abc import ABC, abstractmethod

class data_file(ABC):
    """Abstract base class for data files"""
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_frame = self.read()

    def read(self):
        try:
            if os.path.splitext(self.file_name)[1] == '.csv':
                return pd.read_csv(self.file_name)
            return pd.read_excel(self.file_name)
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    @abstractmethod
    def clean(self):
        pass

class air_egg(data_file):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.clean()

    def clean(self):
        pass
        #self.data_frame.columns = ['Timestamp', 'Temperature']


#Below is for testing purposes only
if __name__ == "__main__":
    obj = air_egg(r'C:\Users\Joel\Documents\GT Courses\Junior Design\data\air_egg.csv')
    print(obj.data_frame.head())