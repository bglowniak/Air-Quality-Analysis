import os

def basic_stats(df, output_folder):
    df = df.describe()
    fn =  'general_statistics.csv'
    df.to_csv(os.path.join(output_folder, fn))
    return fn