import os

def basic_stats(df, output_folder):
    df = df.describe()
    fn =  'general_statistics.csv'
    df.to_csv(os.path.join(output_folder, fn))
    return fn

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