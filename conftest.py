# pytest fixture file for pyrest
#


import os
import glob
import shutil
import time
import pytest
import json


def load_params_from_json(json_paths):
    """Takes a list of json file paths and returns an aggregated list of the
    contents of all of them

    Args:
        json_paths(list[str]): list of paths to parameter json files

    Returns:
        return_list: list[str]

    """
    return_list = []
    for json_path in json_paths:
        with open(json_path) as f:
            return_list += json.load(f)
    print("json is: " + str(return_list))
    return return_list


def load_ids_from_json(json_paths):
    """

    Args:
        json_paths:

    Returns:
        return_list:

    """

    return_list = []
    for json_path in json_paths:
        with open(json_path) as f:
            param_list = json.load(f)

            # get suite tag from filename
            filename = os.path \
                         .split(json_path)[1]

            name_list = os.path \
                          .splitext(filename)[0] \
                          .split('_')

            suite_name = ' '.join(name_list) \
                            .upper()

            for param in param_list:
                # make sure to include notice of skipped tests in the test ID
                # this way it gets reported both in the log and to the IDE
                if param['skip']:
                    tag = "*SKIPPED* " + suite_name + ": " + param['tag']
                else:
                    tag = suite_name + ": " + param['tag']

                return_list += [tag]
    print("tag list is: " + str(return_list))
    return return_list

def get_test_parameter_file_list():
    """Contains the test parameter file paths

    Returns:
        list[str]

    """

    absolute_current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(absolute_current_file_path)
    test_directory = os.path.join(current_directory, 'test_parameter_files')
    search_pattern = test_directory + "/*.json"
    test_parameter_file_list = glob.glob(search_pattern)
    print("returning test_parameter_file_list: " + str(test_parameter_file_list))
    return test_parameter_file_list


@pytest.fixture(
      params=load_params_from_json(get_test_parameter_file_list()),
      ids=load_ids_from_json(get_test_parameter_file_list())
)
def test_data(request):
    """Loads test params from JSON files then issues to test (one by one)

    Args:
        request: pytest request object

    Returns:
        request.param: Values for individual test

    """
    print("request.param is: {}", request.param)
    yield request.param

