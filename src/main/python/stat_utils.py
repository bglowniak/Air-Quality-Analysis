import os
import pandas as pd

def basic_stats(df, output_folder):
    stats = df.describe()
    stats = round(stats, 2)
    if "entry_id" in stats.columns:
        stats = stats.drop("entry_id", axis=1)
    fn = 'general_statistics.csv'
    outpath = os.path.join(output_folder, fn)
    stats.to_csv(outpath)
    return outpath

def extra_stats(df, output_path):
    #returns 95th percentile
    ucl = df.mean() + 2 * df.std()
    #PM10 = 150 20/50
    #PM2.5 =  12/35 10/25
    #SO2 = 20/500
    #returns number of values above the threshold
    TH10 = (df.clip(10) == df).valuecounts()
    TH12 = (df.clip(12) == df).valuecounts()
    TH20 = (df.clip(20) == df).valuecounts()
    TH25 = (df.clip(25) == df).valuecounts()
    TH35 = (df.clip(35) == df).valuecounts()
    TH50 = (df.clip(50) == df).valuecounts()
    TH500 = (df.clip(500) == df).valuecounts()
    # create dataframe with each statistic
    stats_frame = pd.DataFrame([ucl, TH10, TH12, TH20, TH25, TH35, TH50, TH500])
    stats_name = 't_statistics.csv'
    stats_frame.to_csv(os.path.join(output_path, stats_name))
    return stats_name

def above_threshold_stats(df, output_folder):
    
    PM25_24HR_WHO = 25
    PM25_ANNUAL_PRIMARY_WHO = 10
    PM10_24HR_WHO = 50
    PM10_ANNUAL_PRIMARY_WHO = 20

    PM25_24HR_NAAQS = 35
    PM25_ANNUAL_PRIMARY_NAAQS = 12
    PM25_ANNUAL_SECONDARY_NAAQS = 15
    PM10_24HR_NAAQS = 150

    w22 = len(df[df['PM2.5'] >= PM25_24HR_WHO])
    w2a = len(df[df['PM2.5'] >= PM25_ANNUAL_PRIMARY_WHO])
    w102 = len(df[df['PM10.0'] >= PM10_24HR_WHO])
    w10a = len(df[df['PM10.0'] >= PM10_ANNUAL_PRIMARY_WHO])

    n22 = len(df[df['PM2.5'] >= PM25_24HR_NAAQS])
    n2a = len(df[df['PM2.5'] >= PM25_ANNUAL_PRIMARY_NAAQS])
    n2as = len(df[df['PM2.5'] >= PM25_ANNUAL_SECONDARY_NAAQS])
    n102 = len(df[df['PM10.0'] >= PM10_24HR_NAAQS])

    total = len(df.index)

    row0 = ['', '', '', 'Threshold Value', 'Samples Above', 'Percent Above']
    row1 = ['WHO', 'PM 2.5', '24 Hour', '25 ug/m^3', str(w22), "{:.2f}%".format(w22/total)]
    row2 = ['', '', 'Annual Primary', '35 ug/m^3', str(w2a), "{:.2f}%".format(w2a/total)]
    row3 = ['', 'PM 10.0', '24 Hour', '50 ug/m^3', str(w102), "{:.2f}%".format(w102/total)]
    row4 = ['', '', 'Annual Primary', '20 ug/m^3', str(w10a), "{:.2f}%".format(w10a/total)]
    row5 = ['NAAQS', 'PM 2.5', '24 Hour', '35 ug/m^3', str(n22), "{:.2f}%".format(n22/total)]
    row6 = ['', '', 'Annual Primary', '12 ug/m^3', str(n2a), "{:.2f}%".format(n2a/total)]
    row7 = ['', '', 'Annual Secondary', '15 ug/m^3', str(n2as), "{:.2f}%".format(n2as/total)]
    row8 = ['', 'PM 10.0', '24 Hour', '150 ug/m^3', str(n102), "{:.2f}%".format(n102/total)]

    rows = [row0, row1, row2, row3, row4, row5, row6, row7, row8]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(output_folder, 'threshold_stats.csv'))
    return rows

    #      |          |               |  Threshold value  |  Num above  |  Percent above
    # WHO  |  PM 2.5  |      24 HR    |     25 ug/m^3     |    32       |    6%         
    #      |          | Annual Primary|     35 ug/m^3     |    234      |    3%
    #      |  PM 10.0 |      24 HR    |     