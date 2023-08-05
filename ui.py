import easygui
import pathlib


def prompt_for_test_instance_notes():
    return easygui.textbox(
        '''Enter test instance notes.
These notes should, together with with setup description in the spec, be enough to determine the exact setup.
Typical examples of information that should be included:
    - The part number of the unit under test
    - Any modifications done to the test object or setup not specified in the spec''')


def ask_user_for_force_run():
    return easygui.ccbox(
        '''Warning! The current test repo is dirty.
Running the test will not produce traceable results.''',
        choices=("Force run dirty test", "Abort"))


def select_file_in_dir(dir, on_select_func=None) -> pathlib.Path:
    from automated_test_logger import AutomatedTestLogger
    dir_path = pathlib.Path(dir)
    assert(dir_path.is_dir())
    paths = [path for path in dir_path.iterdir() if path.is_file() and path.name.endswith(AutomatedTestLogger.LOG_METADATA_FILE_SUFFIX)]
    if len(paths) == 0:
        return None
    if len(paths) == 1:
        return paths[0]
    display_names = [str(path) for path in paths]
    display_names.reverse()
    choice = easygui.choicebox(msg=None, title="Select log to show", choices=display_names, preselect=0)
    if choice is None:
        return None
    if on_select_func is not None:
        on_select_func(choice)
    return pathlib.Path(choice)
