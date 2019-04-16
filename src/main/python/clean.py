import os
import dateutil.parser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    @param averaging_range: string or python time object for averaging range

    @result String filepath for resulting PDF file
    '''
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    #a little hacky but does the trick for now
    try:
        data_obj = Data_File(filepath, output_path, start_time, stop_time)
    except IOError as e:
        print("IO error!")
        return e
    except Exception as e:
        print("Unknown Error!!")
        print(e)
        return e

    return data_obj.output_fn

class Data_File():
    '''Data File Class - handles file processing automatically upon creation

    @param filepath: the path to the input file
    @param output_path: the folder path for outputting files

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

def filter_on_time(df, start_time=None, stop_time=None):
    #currently broken due to timezone naiive and aware datetime objects
    '''if start_time is not None and stop_time is not None:
        #filter on both
        after_start = df['Datetime'] >= start_time.toPyDateTime()
        before_end = df['Datetime'] <= stop_time.toPyDateTime()
        return df[after_start and before_end]'''
    return df

def parse_time_string(s):
    d = dateutil.parser.parse(s)
    return d

def basic_stats(df, output_path, file_mod):
    df = df.describe()
    fn =  file_mod + '_statistics.csv'
    df.to_csv(os.path.join(output_path, fn))
    return fn

def boxplot(df, output_path, file_mod):
    #simple version, only makes the 4 boxplots every dataset has in common
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
    #fig.suptitle('Air Beam', fontsize=20)
    dat = [df['Temperature'].dropna()]
    ax1.boxplot(dat, labels = ['Temperature'], vert = True)
    dat = [df['Humidity'].dropna()]
    ax2.boxplot(dat, labels = ['Humidity'], vert = True)
    dat = [df['PM2.5'].dropna()]
    ax3.boxplot(dat, labels = ['PM 2.5'], vert = True)
    dat = [df['PM10.0'].dropna()]
    ax4.boxplot(dat, labels = ['PM 10.0'], vert = True)
    fig.subplots_adjust(wspace=0.5)
    outpath = os.path.join(output_path, file_mod + '_boxplot.png')
    fig.savefig(outpath)
    return outpath

def threshold_graph(df, output_path, file_mod):
    plt.close()
    f, axarr = plt.subplots(2, figsize=[10,8], sharex = True)
    axarr[0].plot(df['Datetime'], df['PM2.5'], label='PM 2.5')
    axarr[0].plot(df['Datetime'], df['PM10.0'], label='PM 10.0')
    axarr[0].hlines(25, df['Datetime'][0], df['Datetime'].tail(1), color='r', linestyles='dashed', label='Threshold')
    axarr[0].legend()
    axarr[0].set_title('Particulate Matter and Humidity')
    axarr[1].plot(df['Datetime'], df['Humidity'], label='Humidity (percent)')
    #plt.xticks([df['Datetime'][0], df['Datetime'][5000], df['Datetime'][10000]])
    axarr[1].legend()
    fn = file_mod + '_threshold_graph.png'
    outpath = os.path.join(output_path, fn)
    plt.savefig(outpath, dpi='figure')
    return outpath

#Below is for testing purposes only
if __name__ == "__main__":
    python_folder = os.path.dirname(os.path.abspath(__file__))
    main_folder = os.path.dirname(python_folder)
    src_folder = os.path.dirname(main_folder)
    app_folder = os.path.dirname(src_folder)

    for i in ['Air_beam_7_31_8.22', 'air_egg', 'Purple_air']:
        filename = os.path.join(app_folder, r'data/' + i + '.csv')
        process_file(filename, r'C:\Users\Joel\Documents\GT Courses\Junior Design\Air-Quality-Analysis\data\data_out')