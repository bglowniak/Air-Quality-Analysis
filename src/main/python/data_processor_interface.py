import abc
import enum
import datetime


class DataColumn(enum.Enum):
    TEMPERATURE = 'temperature'
    HUMIDITY = 'humidity'
    DEW_POINT = 'dew point'
    SO2_CONCENTRATION = 'sulfur dioxide concentration'


class DataProcessor(abc.ABC):
    @abc.abstractmethod
    def process(self,
                data_file_path: str,
                output_folder_path: str,
                selected_data_columns: [DataColumn],
                use_time_range: bool,
                time_range_start: datetime.datetime,
                time_range_end: datetime.datetime,
                averaging_period: datetime.timedelta):
        """
        Processes the given data file and writes a PDF file to the given output_folder_path
        :param data_file_path: The path to the selected data file
        :param output_folder_path: The path to write the final PDF to
        :param selected_data_columns: The data columns selected for processing
        :param use_time_range: Whether or not a time range should be used
        :param time_range_start: When the time range starts
        :param time_range_end: When the time range end
        :param averaging_period: The averaging period for statistics
        """
        pass