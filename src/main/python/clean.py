import os
import dateutil.parser
import pandas as pd
import numpy as np
from enum import Enum
import time

class Sensor(Enum):
    AIR_BEAM = 1
    PURPLE_AIR = 2
    AIR_EGG = 3
    INVALID = 4

def process_file(filepath, output_path=None, start_time=None, stop_time=None, averaging_range=None):
    '''Interface to Front End

    @param filepath: string path to file input
    @param output_path: string path to output directory
    @param start_time: string or python time object for start of range to filter data
    @param stop_time: string or python time object for stop of range to filter data
    @param averaging_range: string or pythong time object for averaging range

    @result String filepath for resulting PDF file
    '''
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    data_obj = Data_File(filepath, output_path)
    return data_obj.output_fn

class Data_File():
    '''Base Data File Class

    @param data_frame: pandas data frame object to set as instance data for this data file
    @attribute sensor_type: Sensor enum value, calculated from identify_file() function
    TODO: remove this? @function clean: must be overwritten in subclass to clean based on object type
    TODO: @function make_pdf: 
    '''
    def read_file(self, filepath):
        #reads file and returns pandas dataframe
        try:
            if os.path.splitext(filepath)[1] == '.csv':
                return pd.read_csv(filepath)
            return pd.read_excel(filepath)
        except FileNotFoundError as fnfe:
            print(fnfe)
        except IOError as ioe:
            print(ioe)

    def identify_file(self, data_frame):
        #figures out file type
        identifier = data_frame.columns[0]
        if identifier == 'sensor:model':
            self.file_mod = 'Air_Beam'
            return Sensor.AIR_BEAM
        if identifier == 'created_at':
            self.file_mod = 'Purple_Air'
            return Sensor.PURPLE_AIR
        if identifier == 'Timestamp':
            self.file_mod = 'Air_Egg'
            return Sensor.AIR_EGG
        return Sensor.INVALID

    def __init__(self, filepath, output_path):
        self.output_path = output_path
        self.data_frame = self.read_file(filepath)
        self.sensor_type = self.identify_file(self.data_frame)
        self.file_mod = self.file_mod + time.strftime("%Y%m%d-%H%M%S")
        self.clean()
        self.store_clean_data()
        self.gen_statistics()
        self.visualize()

    def clean(self):
        if self.sensor_type == Sensor.AIR_BEAM:
            self.data_frame = clean_air_beam(self.data_frame)
        elif self.sensor_type == Sensor.AIR_EGG:
            self.data_frame = clean_air_egg(self.data_frame)
        elif self.sensor_type == Sensor.PURPLE_AIR:
            self.data_frame = clean_purple_air(self.data_frame)
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)
        self.data_frame = self.data_frame.sort_values(by = 'Datetime')
        self.data_frame = self.data_frame.apply(pd.to_numeric, errors='ignore')

    def gen_statistics(self):
        df = self.data_frame.describe()
        fn =  self.file_mod + '_statistics.csv'
        self.output_fn = fn
        df.to_csv(os.path.join(self.output_path, fn))

    def store_clean_data(self):
        #writes clean csv to output path
        fn = self.file_mod + '_cleaned.csv'
        output_filepath = os.path.join(self.output_path, fn)
        self.data_frame.to_csv(output_filepath)

    def visualize(self):
        boxplot(self.data_frame)

def clean_purple_air(data_frame):
    data_frame.columns = ['Datetime', 'entry_id', 'PM1.0', 'PM2.5', 'PM10.0', 'UptimeMinutes', 'RSSI_dbm', 'Temperature', 'Humidity', 'Pm2.5_CF_1_ug/m3']
    return data_frame

def clean_air_egg(data_frame):
    data_frame.columns = ['Datetime', 'Temperature', 'Humidity', 'SO2[ppb]', 'SO2[V]', 'PM1.0', 'PM2.5', 'PM10.0', 'Pressure', 'Latitude', 'Longitude', 'Altitude']
    return data_frame

def clean_air_beam(data_frame):
    #TODO: if the values can change on different runs of this sensor, this will need to be changed to be more dynamic
    #That means using the splits, find the Value name, then add the dataframes to a list, then iterate over that list to merge
    beam = data_frame
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
    data_frame = beam
    return data_frame

def parse_time_string(s):
    d = dateutil.parser.parse(s)
    return d

def boxplot(df):
    pass
   
#Below is for testing purposes only
if __name__ == "__main__":
    python_folder = os.path.dirname(os.path.abspath(__file__))
    main_folder = os.path.dirname(python_folder)
    src_folder = os.path.dirname(main_folder)
    app_folder = os.path.dirname(src_folder)

    for i in ['Air_beam_7_31_8.22', 'air_egg', 'Purple_air']:
        filename = os.path.join(app_folder, r'data/' + i + '.csv')
        process_file(filename, r'C:\Users\Joel\Documents\GT Courses\Junior Design\Air-Quality-Analysis\data\data_out')