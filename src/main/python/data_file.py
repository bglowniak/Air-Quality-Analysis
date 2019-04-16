import os
import time
from enum import Enum

import matplotlib.pyplot as plt
import pandas as pd

from clean_utils import (clean_air_beam, clean_air_egg, clean_purple_air,
                         filter_on_time, parse_time_string)
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
    @attribute output_path: output folder path
    @attribute output_fn: output file name
    @attribute file_mod: the file name addition including timestamp and sensor type

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
        raise ValueError('Invalid input file type')

    def __init__(self, filepath, output_path, start_time=None, stop_time=None):
        self.output_path = output_path
        self.data_frame = self.read_file(filepath)
        self.sensor_type = self.identify_file(self.data_frame)
        self.file_mod = self.file_mod + time.strftime("%Y%m%d-%H%M%S")
        self.clean(start_time, stop_time)
        self.store_clean_data()
        self.gen_statistics()
        self.visualize()

    def clean(self, start_time, stop_time):
        if self.sensor_type == Sensor.AIR_BEAM:
            self.data_frame = clean_air_beam(self.data_frame)
        elif self.sensor_type == Sensor.AIR_EGG:
            self.data_frame = clean_air_egg(self.data_frame)
        elif self.sensor_type == Sensor.PURPLE_AIR:
            self.data_frame = clean_purple_air(self.data_frame)
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(parse_time_string)
        self.data_frame = self.data_frame.sort_values(by = 'Datetime')
        self.data_frame = self.data_frame.apply(pd.to_numeric, errors='ignore')
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(pd.to_datetime)
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(lambda x: x.replace(tzinfo=None))
        self.data_frame = filter_on_time(self.data_frame, start_time, stop_time)

    def gen_statistics(self):
        #calculates statistics
        #writes outputs to file
        #TODO: in finished product, this won't write results, only calculate stats and pass to pdf gen
        self.output_fn = basic_stats(self.data_frame, self.output_path, self.file_mod)
        
    def store_clean_data(self):
        #writes clean csv to output path
        fn = self.file_mod + '_cleaned.csv'
        output_filepath = os.path.join(self.output_path, fn)
        self.data_frame.to_csv(output_filepath)

    def visualize(self):
        boxplot(self.data_frame, self.output_path, self.file_mod)
        threshold_graph(self.data_frame, self.output_path, self.file_mod)
