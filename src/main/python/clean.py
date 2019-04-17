import os
from data_file import Data_File

def process_file(filepath, output_path, averaging_range, start_time=None, stop_time=None, ):
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

    data_obj = Data_File(filepath, output_path, averaging_range, start_time, stop_time)

    return data_obj.get_output_filepath()

#Below is for testing purposes only
if __name__ == "__main__":
    python_folder = os.path.dirname(os.path.abspath(__file__))
    main_folder = os.path.dirname(python_folder)
    src_folder = os.path.dirname(main_folder)
    app_folder = os.path.dirname(src_folder)

    for i in ['Air_beam_7_31_8.22', 'air_egg', 'Purple_air']:
        filename = os.path.join(app_folder, r'data/' + i + '.csv')
        process_file(filename, (1, 'Hour'), r'C:\Users\Joel\Documents\GT Courses\Junior Design\Air-Quality-Analysis\data\data_out')
