import os
import dateutil.parser
import pandas as pd
from enum import Enum

class Color(Enum):
    AIR_BEAM = 1
    PURPLE_AIR = 2
    AIR_EGG = 3

class data_file():
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_frame = self.read()
        self.clean()

    def read(self):
        try:
            if os.path.splitext(self.file_name)[1] == '.csv':
                return pd.read_csv(self.file_name)
            return pd.read_excel(self.file_name)
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    def clean(self):
        #figure out file type, calls correct function
        if self.data_frame.columns[0] == 'sensor:model':
            self.file_type = Color.AIR_BEAM
            self.clean_air_beam()
        elif self.data_frame.columns[0] == 'created_at':
            self.file_type = Color.PURPLE_AIR
            self.clean_purple_air()
        elif self.data_frame.columns[0] == 'Timestamp':
            self.file_type = Color.AIR_EGG
            self.clean_air_egg()

    def clean_purple_air(self):
        self.data_frame.columns = ['Datetime', 'entry_id', 'PM1.0', 'PM2.5', 'PM10.0', 'UptimeMinutes', 'RSSI_dbm', 'Temperature', 'Humidity', 'Pm2.5_CF_1_ug/m3']
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)

    def clean_air_egg(self):
        self.data_frame.columns = ['Datetime', 'Temperature', 'Humidity', 'SO2[ppb]', 'SO2[V]', 'PM1.0', 'PM2.5', 'PM10.0', 'Pressure', 'Latitude', 'Longitude', 'Altitude']
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)

    def clean_air_beam(self):
        #TODO: if the values can change on different runs of this sensor, this will need to be changed to be more dynamic
        #That means using the splits, find the Value name, then add the dataframes to a list, then iterate over that list to merge
        beam = self.data_frame
        splits = list(beam[beam['sensor:model'] == 'sensor:model'].index)
        df1 = beam.iloc[0:splits[0]]
        df2 = beam.iloc[splits[0]:splits[1]]
        df3 = beam.iloc[splits[1]:splits[2]]
        df4 = beam.iloc[splits[2]:splits[3]]
        df1.columns = ['Datetime', 'Latitude', 'Longitude', 'Temperature']
        df1 = df1.drop([0,1])
        df2.columns = ['Datetime', 'Latitude', 'Longitude', 'Humidity']
        df2 = df2.drop(df2.index[0:3])
        df3.columns = ['Datetime', 'Latitude', 'Longitude', 'PM2.5']
        df3 = df3.drop(df3.index[0:3])
        df4.columns = ['Datetime', 'Latitude', 'Longitude', 'PM10.0']
        df4 = df4.drop(df4.index[0:3])
        beam = pd.merge(df1, df2, how='outer', on=['Datetime', 'Latitude', 'Longitude'])
        beam = pd.merge(beam, df3, how='outer', on=['Datetime', 'Latitude', 'Longitude'])
        beam = pd.merge(beam, df4, how='outer', on=['Datetime', 'Latitude', 'Longitude'])
        beam['Datetime'] = beam['Datetime'].apply(parse_time_string)
        self.data_frame = beam

def parse_time_string(s):
    d = dateutil.parser.parse(s)
    return d

#Below is for testing purposes only
if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(__file__))
    dirname, _ = os.path.split(dirname)
    for i in ['Air_beam_7_31_8.22', 'air_egg', 'Purple_air']:
        filename = os.path.join(dirname, r'data/' + i + '.csv')
        obj = data_file(filename)
        print(obj.data_frame.head())