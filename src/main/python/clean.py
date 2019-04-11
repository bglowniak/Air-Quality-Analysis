import os
import dateutil.parser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
import time
from datetime import datetime

class SensorType(Enum):
    AIR_BEAM = 'Air_Beam'
    PURPLE_AIR = 'Purple_Air'
    AIR_EGG = 'Air_Egg'
    INVALID = None


class OutputFileTypes(Enum):
    VISUALIZATION_BOXPLOT = 'visualization_boxplot'
    VISUALIZATION_THRESHOLD_GRAPH = 'visualization_threshold_graph'
    STATISTICS_BASIC = 'statistics_basic'


class ProgressUpdate(object):
    def __init__(self, percentage, message):
        self.percentage = percentage
        self.message = message


class DataFileProcessor(object):
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

    def __init__(self, filepath, output_path_enclosing_folder, start_time=None, stop_time=None, averaging_range=None):
        # Assign instance variables
        self.data_file_path = filepath
        self.output_path_enclosing_folder = output_path_enclosing_folder
        self.start_time = start_time
        self.stop_time = stop_time
        self.averaging_range = averaging_range

        self.process_start_time = None
        self.data_frame = None
        self.visualization_figures = {}
        self.statistics_data_frame = None
        self.output_file_paths = {}

    @property
    def _base_output_folder_dir(self):
        dir = os.path.join(self.output_path_enclosing_folder, self._file_mod)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    @property
    def _file_mod(self):
        return '%s-%s' % (self.sensor_type, self.process_start_time.strftime('%Y%m%d-%H%M%S'))

    def process(self):
        self.process_start_time = datetime.now()
        
        file_is_csv = os.path.splitext(self.data_file_path)[1] == '.csv'
        if file_is_csv:
            self.data_frame = pd.read_csv(self.data_file_path)
        else:
            self.data_frame = pd.read_excel(self.data_file_path)

        yield ProgressUpdate(10, 'Read data frame from %s file.' % ('CSV' if file_is_csv else 'Excel'))

        identifier = self.data_frame.columns[0]
        if identifier == 'sensor:model':
            self.sensor_type = SensorType.AIR_BEAM
        elif identifier == 'created_at':
            self.sensor_type = SensorType.PURPLE_AIR
        elif identifier == 'Timestamp':
            self.sensor_type = SensorType.AIR_EGG
        else:
            raise ValueError('Invalid input file type. Identifier is unknown: %s' % identifier)

        yield ProgressUpdate(20, 'Determined sensor type as %s' % self.sensor_type)

        # Get data frame
        if self.sensor_type == SensorType.AIR_BEAM:
            self._clean_air_beam()
        elif self.sensor_type == SensorType.AIR_EGG:
            self._clean_air_egg()
        elif self.sensor_type == SensorType.PURPLE_AIR:
            self._clean_purple_air()

        yield ProgressUpdate(30, 'Cleaned data')

        # Format the data frame accordingly
        progress_updates_required_for_parsing_datetime_values = 10

        for i, datetime_str in enumerate(self.data_frame['Datetime']):

            if i % int(len(self.data_frame['Datetime']) / progress_updates_required_for_parsing_datetime_values) == 0:
                out_of_hundred = (progress_updates_required_for_parsing_datetime_values * i / int(len(self.data_frame['Datetime']) / progress_updates_required_for_parsing_datetime_values))
                percentage = int((50 - 30) * (out_of_hundred / 100) + 30)
                message = 'Parsed %d percent of datetime values' % percentage
                yield ProgressUpdate(percentage, message)

            self.data_frame['Datetime'][i] = dateutil.parser.parse(datetime_str)

        yield ProgressUpdate(50, 'Parsed date time values')
        self.data_frame = self.data_frame.sort_values(by='Datetime')
        yield ProgressUpdate(53, 'Sorted data frame by Datetime field')
        self.data_frame = self.data_frame.apply(pd.to_numeric, errors='ignore')
        yield ProgressUpdate(56, 'Converted data frame to numeric values')
        self.data_frame['Datetime'] = self.data_frame['Datetime'].apply(pd.to_datetime)
        yield ProgressUpdate(58, 'Converted date time values to Python datetime objects')
        self.data_frame = filter_on_time(self.data_frame, self.start_time, self.stop_time)
        yield ProgressUpdate(60, 'Filtered data frame on provided start and stop times')

        # Generate statistics
        self.output_file_paths[OutputFileTypes.STATISTICS_BASIC] = os.path.join(
            self._base_output_folder_dir,
            '%s_%s.csv' % (self._file_mod, OutputFileTypes.STATISTICS_BASIC),
        )
        self.data_frame.describe() \
            .to_csv(self.output_file_paths[OutputFileTypes.STATISTICS_BASIC])

        yield ProgressUpdate(70, 'Generated statistics')

        # Generate visualizations

        # Box plot

        # simple version, only makes the 4 boxplots every dataset has in common
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
        # fig.suptitle('Air Beam', fontsize=20)
        dat = [self.data_frame['Temperature'].dropna()]
        ax1.boxplot(dat, labels=['Temperature'], vert=True)
        dat = [self.data_frame['Humidity'].dropna()]
        ax2.boxplot(dat, labels=['Humidity'], vert=True)
        dat = [self.data_frame['PM2.5'].dropna()]
        ax3.boxplot(dat, labels=['PM 2.5'], vert=True)
        dat = [self.data_frame['PM10.0'].dropna()]
        ax4.boxplot(dat, labels=['PM 10.0'], vert=True)
        fig.subplots_adjust(wspace=0.5)

        self.output_file_paths[OutputFileTypes.VISUALIZATION_BOXPLOT] = os.path.join(
            self._base_output_folder_dir,
            '%s_%s.png' % (self._file_mod, OutputFileTypes.VISUALIZATION_BOXPLOT),
        )
        fig.savefig(self.output_file_paths[OutputFileTypes.VISUALIZATION_BOXPLOT])

        yield ProgressUpdate(80, 'Saved box plot')

        # Threshold Graph

        plt.close()
        f, axarr = plt.subplots(2, figsize=[10, 8], sharex=True)
        axarr[0].plot(self.data_frame['Datetime'], self.data_frame['PM2.5'], label='PM 2.5')
        axarr[0].plot(self.data_frame['Datetime'], self.data_frame['PM10.0'], label='PM 10.0')
        axarr[0].hlines(25, self.data_frame['Datetime'][0], self.data_frame['Datetime'].tail(1), color='r', linestyles='dashed', label='Threshold')
        axarr[0].legend()
        axarr[0].set_title('Particulate Matter and Humidity')
        axarr[1].plot(self.data_frame['Datetime'], self.data_frame['Humidity'], label='Humidity (percent)')
        # plt.xticks([df['Datetime'][0], df['Datetime'][5000], df['Datetime'][10000]])
        axarr[1].legend()

        self.output_file_paths[OutputFileTypes.VISUALIZATION_THRESHOLD_GRAPH] = os.path.join(
            self._base_output_folder_dir,
            '%s_%s.png' % (self._file_mod, OutputFileTypes.VISUALIZATION_THRESHOLD_GRAPH),
        )
        fig.savefig(self.output_file_paths[OutputFileTypes.VISUALIZATION_THRESHOLD_GRAPH])

        yield ProgressUpdate(90, 'Saved threshold graph')

        yield ProgressUpdate(100, 'Generated PDF')

    def _clean_purple_air(self):
        self.data_frame.columns = [
            'Datetime',
            'entry_id',
            'PM1.0',
            'PM2.5',
            'PM10.0',
            'UptimeMinutes',
            'RSSI_dbm',
            'Temperature',
            'Humidity',
            'Pm2.5_CF_1_ug/m3',
        ]

    def _clean_air_egg(self):
        self.data_frame.columns = [
            'Datetime',
            'Temperature',
            'Humidity',
            'SO2[ppb]',
            'SO2[V]',
            'PM1.0',
            'PM2.5',
            'PM10.0',
            'Pressure',
            'Latitude',
            'Longitude',
            'Altitude',
        ]

    def _clean_air_beam(self):
        # TODO: if the values can change on different runs of this sensor, this will need to be changed to be more dynamic
        # That means using the splits, find the Value name, then add the dataframes to a list, then iterate over that list to merge
        splits = list(self.data_frame[self.data_frame['sensor:model'] == 'sensor:model'].index)
        df1 = self.data_frame.iloc[0:splits[0]]
        df2 = self.data_frame.iloc[splits[0]:splits[1]]
        df3 = self.data_frame.iloc[splits[1]:splits[2]]
        df4 = self.data_frame.iloc[splits[2]:splits[3]]
        df1.columns = ['Datetime', 'Latitude', 'Longitude', 'Temperature']
        df1 = df1.drop([0, 1])
        df2.columns = ['Datetime', 'Latitude', 'Longitude', 'Humidity']
        df2 = df2.drop(df2.index[0:3])
        df3.columns = ['Datetime', 'Latitude', 'Longitude', 'PM2.5']
        df3 = df3.drop(df3.index[0:3])
        df4.columns = ['Datetime', 'Latitude', 'Longitude', 'PM10.0']
        df4 = df4.drop(df4.index[0:3])
        self.data_frame = pd.merge(df1, df2, how='outer', on=['Datetime', 'Latitude', 'Longitude'])
        self.data_frame = pd.merge(self.data_frame, df3, how='outer', on=['Datetime', 'Latitude', 'Longitude'])
        self.data_frame = pd.merge(self.data_frame, df4, how='outer', on=['Datetime', 'Latitude', 'Longitude'])


def filter_on_time(df, start_time=None, stop_time=None):
    # currently broken due to timezone naiive and aware datetime objects
    '''if start_time is not None and stop_time is not None:
        #filter on both
        after_start = df['Datetime'] >= start_time.toPyDateTime()
        before_end = df['Datetime'] <= stop_time.toPyDateTime()
        return df[after_start and before_end]'''
    return df


# Below is for testing purposes only
if __name__ == "__main__":
    python_folder = os.path.dirname(os.path.abspath(__file__))
    main_folder = os.path.dirname(python_folder)
    src_folder = os.path.dirname(main_folder)
    air_quality_analysis_folder = os.path.dirname(src_folder)

    for sample_data_file in ['Air_beam_7_31_8.22.csv', 'air_egg.csv', 'Purple_air.csv']:
        filename = os.path.join(air_quality_analysis_folder, 'data', sample_data_file)
        data_out_directory = os.path.join(air_quality_analysis_folder, 'data', 'data_out')
        data_file_processor = DataFileProcessor(filename, data_out_directory)

        for progress_update in data_file_processor.process():
            print(progress_update.percentage, progress_update.message)

        print(data_file_processor.output_file_paths)
