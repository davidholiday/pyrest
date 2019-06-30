# pyREST

## WHAT IS? 
This is a [pytest](https://docs.pytest.org/en/latest/) framework that allows for testing server responses to queries. Define RESTful queries in JSON and what is supposed to come back as a result. The framework allows for chaining requests together to facillitate user-story validation. 


## HOW TO SET UP? 
Create a virtual environment and use the requirements file in the project directory to install what's needed into your venv sandbox. See [this](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) for help on dealing with virtualenv.  


## HOW TO RUN?
In pycharm or the terminal you can run this like any other pytest. If running at the command line get into the root project directory and execute the following command:
 `pytest -s ` (omit the `-s` flag if you don't want log data printed to the terminal).

## HOW TO WRITE NEW TESTS? 

pyREST considers a json test file to be a *suite* of tests and each json block in the file to be an individual test. To add new tests, either create a new suite file and add the test definition to it or add a new test definition block to an existing suite test file located in `./test_parameter_files`. the naming convention: **pyrest_{name of suite}_test_parameters.json**. It is important that you follow this naming convention as failure to do so will dork up the frameworks' ability to pick up the suite name.

### what is meant by 'a properly formatted json block?'
This is an example of a properly formatted json block. Note that the test logic expects all keys to be represented, even if there are no values associated with them: 

```  
  {
    "purpose": "SETUP",
    "tag" : "user should be able to log out",
    "skip": false,
    "http_verb": "POST",
    "payload": {
      "username": "Grizzly",
      "password": "adam$"
    },
    "files": {},
    "url": "https://localhost:3000/user/login",
    "expected_response_status_code": 200,
    "expected_response_headers_content_type": "application/json; charset=utf-8",
    "expected_response_json": {
      "user": 1,
      "status": "Login successful!"
    },
    "expected_response_json_type_check": {},
    "retain_response_keys": [],
    "subsequent_request": {
      "purpose": "TEST",
      "tag" : "user should be able to log out",
      "skip": false,
      "http_verb": "GET",
      "payload": {},
      "files": {},
      "url": "https://localhost:3000/user/logout",
      "expected_response_status_code": 200,
      "expected_response_headers_content_type": "application/json; charset=utf-8",
      "expected_response_json": {
        "status": "Logout successful!"
      },
      "expected_response_json_type_check": {},
      "retain_response_keys": [],
      "subsequent_request": {}
      }
  }
  ```

**EXPLANATION OF KEYS:**

* purpose: Because pytest will view everything in this block as one test, the 'purpose' field allows the test engineer to put an indicator in the log that will distinguish the calls from one another. 

* tag: short description of what the test is doing

* skip: If true, the framework will skip this test. This is necessaary because pytest can't, in this case, can't provide a test-level of granularity with respect to skipping tests. 

* payload: if you're PUTing or POSTing to a server, this is where you'll supply the data that's being sent serverside. 

* files: The location and name of a file you want to upload to the server. 

* url: the url of the server you wish to communicate with.

* expected_response_status_code: the status code you expect the server send back in response to your request. 

* expected_response_headers_content_type: the headers and content type you expect the server to send back in response to your request. 

* expected_response_json: the body of the response you expect the server to send back in reply to your request.

* expected_response_json_type_check: the key and type of object you expect the server to send back in response to your request. 
 
 * retain_response_keys: the key (see below) of the response value you want the framework to retain and pass along to a subsequent call to the server. It takes the form of `{ HTTP_VERB: KEY }`. depending on the value of _HTTP_VERB_, the test logic will make some assumptions about what to do with those retained values. for _GET_ requests, it is assumed that all retained values are path parameters and as such will be appended to the url of the subsequent request. for _POST_ requests, retained values will be appended to the body of the subsequent request. 
 
 * subsequent_request: a follow up request you want the framework to make that's within the scope of the current test. For example, if you are testing an endpoint that modifies an entry in a database table, the first call would be to modify the data and the subsequent call would be to the endpoint that retrieves the data from the database so you can verify the modification actually happened and happened correctly.  


## LIMITATIONS AND OTHER GOTCHAS 

* For tests that reference mock input/output files, it matters what kind of test you're creating when you specify the location of the testing files. Sometimes the file needs to be referenced with respect to the server's location in the filesystem, whereas other times those files need to be referenced with respect to the location of file `api_endpoints_test.py`.

* Only _GET_ and _POST_ are supported for retained response values.

* For both type-check-only tests and tests that require a server response value be passed to a subsequent call, the server's response can not be in the form of a list. 

* You can only include one file in the 'files' section of the test parameter block. 

* response type checking currently supports str, int, and unicode only.
