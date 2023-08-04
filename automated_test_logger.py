import pathlib
import __main__
import json
import os
from datetime import datetime
import functools

from file_backed_dict import FileBackedDict
from git_info import GitInfo
import ui


def get_time_str():
    return datetime.now().strftime(AutomatedTestLogger.TIME_FORMAT)


def get_time_str_for_filename():
    return datetime.now().strftime(AutomatedTestLogger.FILENAME_TIME_FORMAT)


class AutomatedTestLogger:
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    FILENAME_TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
    SPEC_FILE_SUFFIX = 'spec.*'
    LOG_METADATA_FILE_SUFFIX = 'metadata.json'
    LOG_DATA_FILE_SUFFIX = 'data.csv'
    FILENAME_DELIMITER = '_'
    CSV_DELIMITER = ';'
    CSV_COLUMNS = ['timestamp', 'class_name', 'function_name', 'args', 'return_val']
    DEFAULT_LOG_DIR = 'logs'

    def __init__(self, require_spec_file=True, procedure_id=None):
        git_info = GitInfo()

        if (git_info.is_dirty and not ui.ask_user_for_force_run()):
            exit()

        test_path = pathlib.Path(__main__.__file__)
        test_name = test_path.stem
        test_dir = test_path.parent.relative_to(git_info.git_local_dir)

        log_dir_path = test_dir.joinpath(self.DEFAULT_LOG_DIR)
        if not pathlib.Path(log_dir_path).exists():
            os.mkdir(log_dir_path)

        test_name_including_procedure_id = test_name if procedure_id is None else f'{test_name}{self.FILENAME_DELIMITER}{procedure_id}'
        log_metadata_filename = log_dir_path.joinpath((self.FILENAME_DELIMITER).join(
            [test_name_including_procedure_id, get_time_str_for_filename(), self.LOG_METADATA_FILE_SUFFIX]))
        self._log_data_path = log_dir_path.joinpath((self.FILENAME_DELIMITER).join(
            [test_name_including_procedure_id, get_time_str_for_filename(), self.LOG_DATA_FILE_SUFFIX]))
        
        spec_file_pattern = f'{test_name}{self.FILENAME_DELIMITER}{self.SPEC_FILE_SUFFIX}'
        spec_files = list(test_dir.glob(spec_file_pattern))
        spec_files_names_str = '\n\t'.join([str(x) for x in spec_files])
        assert len(spec_files) <= 1, f"Error: Multiple spec files found:{spec_files_names_str}"
        assert spec_files or (not require_spec_file), f"Error: Could not find spec file matching {spec_file_pattern} in {test_dir}"
        spec_filename = str(spec_files[0]) if spec_files else None

        metadata = {
            'test_start': get_time_str(),
            'git-hash': git_info.git_hash,
            'git-url': git_info.git_url,
            'dirty': git_info.is_dirty,
            'spec_filename': spec_filename,
            'log_data_filename': str(self._log_data_path),
            'log_metadata_filename': str(log_metadata_filename),
            'test_instance_notes': ui.prompt_for_test_instance_notes()}

        self._metadata = FileBackedDict(log_metadata_filename, metadata)

        with open(self._log_data_path, 'w') as f:
            line = self.CSV_DELIMITER.join(self.CSV_COLUMNS)
            f.write(line + '\n')


    def __setitem__(self, key, value):
        self._metadata[key] = value


    def log(self, class_name, function_name, args, return_val):
        def adaptive_json_dumps(obj):
            try:
                return json.dumps(obj)
            except TypeError as e:
                try:
                    class CustomEncoder(json.JSONEncoder):
                        def default(self, o):
                            return o.__dict__
                    return json.dumps(obj, cls=CustomEncoder)
                except Exception:
                    raise e

        args = adaptive_json_dumps(args)
        return_val = adaptive_json_dumps(return_val)
        line = self.CSV_DELIMITER.join([f'{x}' for x in [get_time_str(), class_name, function_name, args, return_val]])
        with open(self._log_data_path, 'a') as f:
            f.write(line + '\n')


def use_automated_test_logger(f):
    '''Decorator usable on member functions of classes with a AutomatedTestLogger named `_automated_test_logger`'''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return_val = f(*args, **kwargs)
        # For simplicity of parsing the log file, we log args as kwargs if any kwargs exist
        if(kwargs):
            kwargs.update(zip(f.__code__.co_varnames, args))
            _self = kwargs.pop('self')
            log_args = kwargs
        else:  
            _self = args[0]
            log_args = args[1:] if len(args) > 2 else args[1] if len(args) > 1 else None
        assert hasattr(_self, '_automated_test_logger'), "Decorator not usable, see docstring"  # To prevent silent errors when using the decorator, but not having a correctly named logger
        if _self._automated_test_logger is not None:  # To enable classes to disable logging on the instance-level, the logger is allowed to be None
            _self._automated_test_logger.log(_self.__class__.__name__, f.__name__, log_args, return_val)
        return return_val
    return wrapper