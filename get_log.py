import ui
from automated_test_logger import AutomatedTestLogger
import pathlib
import __main__
import json
from dataclasses import dataclass
from typing import List, Callable, Tuple
from datetime import datetime

@dataclass
class LoggedFunctionCall:
    timestamp: str
    class_name: str
    function_name: str
    args: any
    return_val: any


@dataclass
class Log:
    metadata: dict
    data: List[LoggedFunctionCall]


def try_json_loads(val):
    try:
        return json.loads(val)
    except Exception as e:
        return val


def get_log(logs_dir = None) -> Log:
    log = Log(None, [])
    logs_dir = logs_dir if logs_dir is not None else pathlib.Path(__main__.__file__).parent.joinpath(AutomatedTestLogger.DEFAULT_LOG_DIR)
    log_metadata_filename = ui.select_file_in_dir(logs_dir)
    with open(log_metadata_filename) as f:
        log.metadata = json.loads(f.read())
    log_data_filename = log.metadata['log_data_filename']
    with open(log_data_filename) as f:
        for line in f:
            parts = line.split(AutomatedTestLogger.CSV_DELIMITER)
            log.data.append(LoggedFunctionCall(
                timestamp = parts[0],
                class_name = parts[1],
                function_name = parts[2],
                args = try_json_loads(parts[3]),
                return_val = try_json_loads(parts[4])
            ))
    return log


def get_logged_property_against_time(log: Log, class_name_filter: str = None, function_name_filter: str = None, property_extraction_function : Callable[[any, any], any] = None) -> Tuple[List[datetime], List[any]]:
    def default_extraction_function(args, return_val):
        return return_val
    property_extraction_function = property_extraction_function if property_extraction_function is not None else default_extraction_function
    def filter(class_name, function_name):
        class_match = class_name_filter is None or class_name == class_name_filter
        function_match = function_name_filter is None or function_name == function_name_filter
        return class_match and function_match
    filtered_log_data = [x for x in log.data if filter(x.class_name, x.function_name)]
    t = [datetime.strptime(x.timestamp, AutomatedTestLogger.TIME_FORMAT) for x in filtered_log_data]
    property = [property_extraction_function(x.args, x.return_val) for x in filtered_log_data]
    return t, property


def cross_plot(x_t: List[datetime], x_vals: List[any], y_t: List[datetime], y_vals: List[any]) -> Tuple[List[any], List[any]]:
    """Returns filtered x- and y-values, with the first list containing the closest preceding x-value for every y-value"""
    import bisect
    x_closest_vals = []
    y_vals_filtered = []

    for idx, d in enumerate(y_t):
        pos = bisect.bisect_right(x_t, d)
        if pos:
            x_closest_vals.append(x_vals[pos - 1])
            y_vals_filtered.append(y_vals[idx])

    return x_closest_vals, y_vals_filtered
