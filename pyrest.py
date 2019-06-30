# pyrest runner
#


import logging
import sys
import requests
import urllib3

from os import path
from flask import json
from test_steps import test_logger, eq, ok


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


'''
---------------
TEST HELPERS
---------------
'''

def remove_extraneous_keys_from_actual_response(
        expected_response_json, actual_response_json):
    """ takes two unordered lists of dicts, one in which the dicts contain a
    subset of the keys contained in the other, removes all the extraneous kv
    pairs from all the dicts in the superset list then returns the trimmed list
    to caller.

    Args:
        expected_response_json (list[dict]): list of dicts containing values we
         are checking for in a response to a given REST call. this is the
         'subset' list.

        actual_response_json (list[dict]): list of dicts containing the
          response to a given REST call. this is the 'superset' list.

    Returns:
        a version of the actual_response_json that has only the kv pairs
          represented in expected_response_json

    """
    template_expected_response_dict = expected_response_json[0]

    actual_response_json_subset = []
    for e in actual_response_json:
        actual_response_json_subset += \
            [dict(
                (k, e[k]) for k in template_expected_response_dict if k in e)]

    return actual_response_json_subset


def get_test_data_clone_with_cookie_object(test_data):
    """ returns a clone of test_data dict with a k,v pair for a cookie

    Args:
        test_data (dict): parameters to to create the request

    Returns:
        test_data dict with
    """

    test_data_copy = test_data.copy()
    if 'cookies' not in test_data.keys():
        test_data_copy['cookies'] = {}

    return test_data_copy


def get_request(test_data):
    """ execute GET request given arguments

    Args:
        test_data(dict): parameters to to create the request

    Returns:
        server response
    """

    return requests.get(test_data['url'],
                        verify=False,
                        cookies=test_data['cookies'])


def post_request(test_data):
    """ execute POST request given arguments

    Args:
        test_data(dict): parameters to to create the request

    Returns:
        server response
    """
    if test_data['payload_is_json']:
        return requests.post(test_data['url'],
                             json=test_data['payload'],
                             files=test_data['files'],
                             verify=False,
                             cookies=test_data['cookies'])
    else:
        return requests.post(test_data['url'],
                             data=test_data['payload'],
                             files=test_data['files'],
                             verify=False,
                             cookies=test_data['cookies'])


def put_request(test_data):
    """ execute PUT request given arguments

    Args:
        test_data(dict): parameters to to create the request

    Returns:
        server response
    """
    if test_data['payload_is_json']:
        return requests.put(test_data['url'],
                            json=test_data['payload'],
                            files=test_data['files'],
                            verify=False,
                            cookies=test_data['cookies'])
    else:
        return requests.put(test_data['url'],
                            data=test_data['payload'],
                            files=test_data['files'],
                            verify=False,
                            cookies=test_data['cookies'])


def delete_request(test_data):
    """ execute DELETE request given arguments

    Args:
        test_data(dict): parameters to to create the request

    Returns:
        server response
    """
    if test_data['payload_is_json']:
        return requests.delete(test_data['url'],
                               json=test_data['payload'],
                               verify=False,
                               cookies=test_data['cookies'])
    else:
        return requests.delete(test_data['url'],
                               data=test_data['payload'],
                               verify=False,
                               cookies=test_data['cookies'])


def get_request_dict():
    """ returns a dict that acts like a case statement that switches on
      http verbs

    Returns(dict): k: http verb as string, v: function that takes a parameter
      dict as an argument and uses it to submit an http request
    """

    return {'GET': get_request,
            'POST': post_request,
            'PUT': put_request,
            'DELETE': delete_request
            }


def get_type_dict():
    """ returns s dict that pairs type name to type object

    Returns(dict):

    """

    return {'str': type(''),
            'int': type(0),
            'unicode': type(u'')
            }


'''
---------------
TEST LOGIC
---------------
'''


def test_api_endpoints(test_data):
    """ common REST API test logic that hits a given endpoint and checks
    actual results against what's expected

    Args:
        test_data (dict): blocks of test parameters supplied one at a
          time by the test_data fixture

        'retained_responses' (dict): when multiple requests are made by a test,
          this allows a preceding request to pass server response values to
          this allows a preceding request to pass server response values to
          subsequent calls

    Returns:

    """
    test_logger.info("test_data is: {}", test_data)
    # eject if caller wants to skip this test
    if test_data['skip']:
        return

    # check for retained responses from previous calls. this is used to allow
    # subsequent requests to access a resource created by a previous one.
    # values that are saved for a subsequent GET request are assumed to be path
    # parameters and are appended to the URL as such. values that are saved for
    # POST requests are appended to the body of the request object.
    if 'retained_responses' in test_data:

        for http_verb, retained_response_kv_dict \
                in test_data['retained_responses'].iteritems():

            if http_verb == 'GET':
                for e in retained_response_kv_dict:
                    for k, v in e.iteritems():
                        new_url = test_data['url'] + '/' + str(v)
                        test_logger.info("updating url to: " + new_url)
                        test_data['url'] = new_url

            elif http_verb == 'POST':
                for e in retained_response_kv_dict:
                    for k, v in e.iteritems():

                        test_logger.info(
                            "adding %s %s to body of POST request " % (k, v))

                        test_data['payload'][k] = v

    # make request to server
    test_logger.info("REQUEST PURPOSE: " + test_data['purpose'])
    test_logger.info("test_data is: " + str(test_data))

    request_dict = get_request_dict()
    http_verb = test_data['http_verb']

    # if need be resolve file name string to actual file object
    # don't forget that type(http_verb) is unicode, not str so '=='
    # instead of 'is' !!
    if http_verb == 'POST' and len(test_data['files']) is not 0:
        filename = path.join(
            path.dirname(path.abspath(__file__)),
            str(test_data['files']['file'])
        )
        print('FILENAME', filename)
        test_data['files']['file'] = open(filename, 'rb')

    # nest payload dicts
    # format selected_path key if exists
    # might be able to remove with flask depending on how payloads are parsed
    if http_verb == 'POST' and 'selected_path' \
            in test_data['payload']:
        test_data['payload']['selected_path'] = \
            json.dumps(test_data['payload']["selected_path"])

    test_data = get_test_data_clone_with_cookie_object(test_data)
    response = request_dict[http_verb](test_data)

    try:
        test_logger.debug("server response is: " +
                          json.dumps(response.json(), indent=2))
    except:
        test_logger.warn("not logging server response, probably because it's "
                         "a file object...")

    # check explicit actual v expected server responses
    eq(response.status_code, test_data['expected_response_status_code'],
       "server should respond with HTTP OK")

    response_content_type = response.headers['Content-Type']
    eq(response_content_type,
       test_data['expected_response_headers_content_type'],
       "content type should match expected")

    expected_response_json = test_data['expected_response_json']

    # because the download endpoint doesn't return json
    if response_content_type == 'text/csv; charset=utf-8':
        actual_response_json = {}
    else:
        actual_response_json = response.json()

    # b/c response to a GET request vs process id is sometimes a nested dict
    if 'process' in actual_response_json and \
            isinstance(actual_response_json['process'], dict):
        actual_response_json = actual_response_json['process']

    if isinstance(expected_response_json, list):
        # for many of the test cases we're only able to check for
        # a subset of the kv pairs a given endpoint plops out. moreover the
        # server can't be counted on to return things in a predictable order.
        # therefore, in order to efficiently perform comparison, we're going to
        # figure out what kv pairs we're expecting and remove the remainder
        # from what the endpoint returns.
        actual_response_json_subsets = \
            remove_extraneous_keys_from_actual_response(
                expected_response_json, actual_response_json)

        for e in expected_response_json:
            ok(e in actual_response_json_subsets,
               "server response should contain expected server response: " +
               str(actual_response_json_subsets) + " " + str(e))
    else:
        for k in expected_response_json:
            eq(actual_response_json[k], expected_response_json[k],
               "server response should match expected server response")

    # check type-check-only values
    #
    # *NOTE* this works because it assumes that there won't be a case where
    # we're doing these kinds of type-only checks when actual_response_json is
    # list. if that changes this (and probably the above block as well)
    # will need to be refactored
    if len(test_data['expected_response_json_type_check']) is not 0:
        type_dict = get_type_dict()

        for k, v in test_data['expected_response_json_type_check'].iteritems():
            actual_response_value = actual_response_json[k]
            expected_type = type_dict[v]

            eq(type(actual_response_value), expected_type,
               "server response type should match "
               "expected server response type")

    # build retained_responses dict for subsequent requests.
    #
    # *NOTE* this block assumes that actual_response_json is a dict,
    # not a list. retained responses, if any, will be transformed into:
    #  {
    #      HTTP_VERB : [ {retained_response_key: retained_response_value}, ...]
    #  }
    retained_responses = {}

    # b/c for some reason python interprets an empty {} in a json block a list
    retain_response_keys = dict(test_data['retain_response_keys'])


    # what a given REST call returns may not map to the same k,v pair a
    # subsequent call is expecting. this block reads the test parameter file
    # and makes the appropriate translation
    for http_verb, retain_response_key_dict in retain_response_keys.iteritems():

        retained_response_kv_list = []
        for response_key, subsequent_request_key in \
                retain_response_key_dict.iteritems():

            test_logger.info(actual_response_json)
            retained_response_element = {
                subsequent_request_key: actual_response_json[response_key]
            }

            retained_response_kv_list.append(retained_response_element)

        retained_responses[http_verb] = retained_response_kv_list


    # if present execute follow-up request
    subsequent_request = test_data['subsequent_request']
    if len(subsequent_request) is not 0:
        subsequent_request['retained_responses'] = retained_responses

        if len(test_data['cookies']) is 0:
            subsequent_request['cookies'] = response.cookies
        else:
            subsequent_request['cookies'] = test_data['cookies']

        test_api_endpoints(subsequent_request)
