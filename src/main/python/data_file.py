import os
import time
from enum import Enum

import matplotlib.pyplot as plt
import pandas as pd

from clean_utils import (clean_air_beam, clean_air_egg, clean_purple_air,
                         filter_on_time, parse_time_string, resample)
from stat_utils import basic_stats
from vis_utils import boxplot, threshold_graph


class Sensor(Enum):
    AIR_BEAM = 1
    PURPLE_AIR = 2
    AIR_EGG = 3
    INVALID = 4

class Data_File():
    '''Data File Class - handles file processing automatically upon creation

    @param filepath: the path to the input file
    @param outupt_path: the folder path for outputting files

    @attribute sensor_type: Sensor enum value, calculated from identify_file() function
    @attribute data_frame: data stored in a pandas DataFrame object
    @attribute output_folder: output folder path
    @attribute output_file_path: full output file path
    @attribute averaging_range: tuple containing integer then string indicating time to average values over

    TODO: @function make_pdf: 
    '''
    def __init__(self, filepath, output_path, averaging_range, start_time=None, stop_time=None):
        self.averaging_range = averaging_range
        self.file_dict = {}
        self.data_frame = self.read_file(filepath)
        self.sensor_type = self.identify_file(self.data_frame)
        self.set_output_folder(output_path)
        self.clean(start_time, stop_time)

        self.gen_statistics()
        self.visualize()
        #line below is temporary, will later be removed and changed to pdf
        self.output_file_path = self.output_folder

    def get_output_filepath(self):
        if self.output_file_path is not None:
            return self.output_file_path
        else:
            raise ValueError("output file not created!")
    
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
        #also sets self.output_folder
        identifier = data_frame.columns[0]
        if identifier == 'sensor:model':
            return Sensor.AIR_BEAM
        if identifier == 'created_at':
            return Sensor.PURPLE_AIR
        if identifier == 'Timestamp':
            return Sensor.AIR_EGG
        raise ValueError('Invalid input file type')

    def set_output_folder(self, output_path):
        now = time.strftime("%Y%m%d-%H%M%S")
        if self.sensor_type == Sensor.AIR_BEAM:
            folder_name = 'Air_Beam' + now
        elif self.sensor_type == Sensor.AIR_EGG:
            folder_name = 'Air_Egg' + now
        elif self.sensor_type == Sensor.PURPLE_AIR:
            folder_name = 'Purple_Air' + now
        self.output_folder = os.path.join(output_path, folder_name)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def clean(self, start_time, stop_time):
        #clean data to uniform type
        if self.sensor_type == Sensor.AIR_BEAM:
            self.data_frame = clean_air_beam(self.data_frame)
        elif self.sensor_type == Sensor.AIR_EGG:
            self.data_frame = clean_air_egg(self.data_frame)
        elif self.sensor_type == Sensor.PURPLE_AIR:
            self.data_frame = clean_purple_air(self.data_frame)
        #Parse datetime column to Datetime object
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)
        #Sort data by datetime
        self.data_frame = self.data_frame.sort_values(by = 'Datetime')
        #convert dataframe data from strings to numbers
        self.data_frame = self.data_frame.apply(pd.to_numeric, errors='ignore')
        #since Datetime column was just converted to numbers, reconvert to dates
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(pd.to_datetime)
        #Remove timezone information
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(lambda x: x.replace(tzinfo=None))

        self.data_frame = filter_on_time(self.data_frame, start_time, stop_time)
        self.data_frame = resample(self.data_frame, self.averaging_range)
        self.store_clean_data()

    def gen_statistics(self):
        #calls statistics functions
        stats = basic_stats(self.data_frame, self.output_folder)
        self.file_dict.update({'basic_stats': stats})
        
    def store_clean_data(self):
        #writes clean csv to output path
        fn = 'cleaned_data.csv'
        output_filepath = os.path.join(self.output_folder, fn)
        self.data_frame.to_csv(output_filepath)

    def visualize(self):
        self.file_dict.update({'boxplot': boxplot(self.data_frame, self.output_folder)})
        self.file_dict.update({'threshold_graph': threshold_graph(self.data_frame, self.output_folder)})
