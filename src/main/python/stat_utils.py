import os

def basic_stats(df, output_path, file_mod):
    df = df.describe()
    fn =  file_mod + '_statistics.csv'
    df.to_csv(os.path.join(output_path, fn))
    return fn