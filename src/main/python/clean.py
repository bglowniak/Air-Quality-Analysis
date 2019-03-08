import os
import dateutil.parser
import pandas as pd
from enum import Enum
from abc import ABC, abstractmethod

class Sensor(Enum):
    AIR_BEAM = 1
    PURPLE_AIR = 2
    AIR_EGG = 3
    INVALID = 4

def process_file(filepath, start_time=None, stop_time=None, averaging_range=None):
    '''Interface to Front End

    @param filepath: string path to file input
    @param start_time: string or python time object for start of range to filter data
    @param stop_time: string or python time object for stop of range to filter data
    @param averaging_range: string or pythong time object for averaging range

    @result String filepath for resulting PDF file
    '''
    file_dir = os.path.dirname(filepath)
    #temp
    cleaned_dir = os.path.join(file_dir, 'data_out')
    if not os.path.exists(cleaned_dir):
        os.makedirs(cleaned_dir)
    #temp
    data = read_file(filepath)
    data_type = identify_file(data)
    if data_type == Sensor.AIR_BEAM:
        data_obj = Air_Beam(data)
    elif data_type == Sensor.AIR_EGG:
        data_obj = Air_Egg(data)
    elif data_type == Sensor.PURPLE_AIR:
        data_obj = Purple_Air(data)
    data_obj.clean()
    #data_obj.make_pdf()
    #below is temporary, should be changed in the future
    print(data_obj.data_frame.head())
    return data_obj.write_csv(cleaned_dir, data_type)

def read_file(file_path):
    #reads file and returns pandas dataframe
    try:
        if os.path.splitext(file_path)[1] == '.csv':
            return pd.read_csv(file_path)
        return pd.read_excel(file_path)
    except FileNotFoundError as fnfe:
        print(fnfe)
    except IOError as ioe:
        print(ioe)

def identify_file(data_frame):
    #figures out file type
    identifier = data_frame.columns[0]
    if identifier == 'sensor:model':
        return Sensor.AIR_BEAM
    if identifier == 'created_at':
        return Sensor.PURPLE_AIR
    if identifier == 'Timestamp':
        return Sensor.AIR_EGG
    return Sensor.INVALID

class Data_File(ABC):
    '''Abstract base class for a data file, subclasses must overwrite the clean function

    @param data_frame: pandas data frame object to set as instance data for this data file

    @function clean: must be overwritten in subclass to clean based on object type
    TODO: @function make_pdf: 
    '''
    def __init__(self, data_frame):
        self.data_frame = data_frame

    @abstractmethod
    def clean(self):
        pass

    def write_csv(self, file_dir, data_type):
        #probably should delete this method eventually
        fn = ''
        if data_type == Sensor.AIR_BEAM:
            fn = 'Air_Beam_Output.csv'
        elif data_type == Sensor.PURPLE_AIR:
            fn = 'Purple_Air_Output.csv'
        elif data_type == Sensor.AIR_EGG:
            fn = 'Air_Egg_Output.csv'
        self.data_frame.to_csv(os.path.join(file_dir, fn))

class Purple_Air(Data_File):
    def clean(self):
        self.data_frame.columns = ['Datetime', 'entry_id', 'PM1.0', 'PM2.5', 'PM10.0', 'UptimeMinutes', 'RSSI_dbm', 'Temperature', 'Humidity', 'Pm2.5_CF_1_ug/m3']
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)

class Air_Egg(Data_File):
    def clean(self):
        self.data_frame.columns = ['Datetime', 'Temperature', 'Humidity', 'SO2[ppb]', 'SO2[V]', 'PM1.0', 'PM2.5', 'PM10.0', 'Pressure', 'Latitude', 'Longitude', 'Altitude']
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)

class Air_Beam(Data_File):
    def clean(self):
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
    python_folder = os.path.dirname(os.path.abspath(__file__))
    main_folder = os.path.dirname(python_folder)
    src_folder = os.path.dirname(main_folder)
    app_folder = os.path.dirname(src_folder)

    for i in ['Air_beam_7_31_8.22', 'air_egg', 'Purple_air']:
        filename = os.path.join(app_folder, r'data/' + i + '.csv')
        process_file(filename)