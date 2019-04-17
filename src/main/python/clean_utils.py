import dateutil.parser
import pandas as pd

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
    if start_time is not None and stop_time is not None:
        #filter on both
        after_start = df['Datetime'] >= start_time.toPyDateTime()
        before_end = df['Datetime'] <= stop_time.toPyDateTime()
        return df[after_start & before_end].reset_index(drop=True)
    return df

def parse_time_string(s):
    d = dateutil.parser.parse(s)
    return d

def resample(df, averaging_range):
    rate_num = averaging_range[0]
    rate_str = averaging_range[1]

    rate_in_seconds = (df['Datetime'][1] - df['Datetime'][0]).total_seconds()

    if rate_str == 'Minutes':
        if rate_in_seconds == rate_num*60:
            #if the difference in time of two values is equal to the sample rate, the function below will fail
            print("Cannot resample file at the same rate it is already sampled!!")
            return df
        rate = str(rate_num) + 'T'
    elif rate_str == 'Hours':
        if rate_in_seconds == rate_num*60*60:
            #if the difference in time of two values is equal to the sample rate, the function below will fail
            print("Cannot resample file at the same rate it is already sampled!!")
            return df
        rate = str(rate_num) + 'H'
    elif rate_str == 'Days':
        if rate_in_seconds == rate_num*60*60*24:
            #if the difference in time of two values is equal to the sample rate, the function below will fail
            print("Cannot resample file at the same rate it is already sampled!!")
            return df
        rate = str(rate_num) + 'D'
    else:
        raise ValueError("Averaging Duration must be measured in Minutes, Hours, or Days")

    try:
        df_resampled = df.resample(rate, on='Datetime').mean().reset_index()
        df_resampled = df_resampled.dropna(thresh=2).reset_index(drop=True)
    except MemoryError:
        print('Memory Error due to high resample rate!! Data Resampling Ignored!')
        res = df
    except ValueError:
        print("ValueError at line 82 in clean_utils.py")
    if len(df_resampled) > len(df):
        print("Averaging duration rate is faster than original sample rate. Data Resampling Ignored.")
        res = df
    return res
