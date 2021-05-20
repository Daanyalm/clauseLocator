  
"""I have laid this API over a single page rather than call some of the functions through imports via different files.
    This is because the length (whilst fairly long) will not benefit from a multi-file approach."""

from flask import Flask, request, jsonify
import json
from datetime import datetime,date


"""This class is designed to expand upon the built in Python exception class and allows exception to optionally carry payloads. The primary function of the class is to allow the exception
to easily be converted to dictinary format. The attributes of the exception can also be easily accessed. """
class ExceptionMessage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        message = dict(self.payload or ())
        message['message'] = self.message
        return message


"""The below function validates the request and returns clear and concise error messages with an appropriate status code, in the event of a bad request."""

def input_validation(request_obj):

    if len(request_obj) != 2:
        return 'The number of keys provided in the request is incorrect. keys should be "text" and "sentence" only. Both keys should correspond to string values', True

    try:
        sentence = request_obj['sentence']
        text = request_obj['text']
        if not isinstance(sentence,str) or not isinstance(text,str):
            return 'There is a key present that does not correspond to a string value . Keys should be "text" and "sentence". Both keys should correspond to string values', True
    except (ValueError, KeyError):
        return 'Missing key. Keys should be "text" and "sentence" (case-sensitive). Both keys should correspond to string values', True

    return 'Request validation passed.', False

"""The below function is the core logic for executing the clause locator functionality. It is a separate function, rather than part of the route wrapper function, in order to
    separate functionality and make the code easy to read."""

def evaluate_result(text,sentence): 

    result_string = ''
    best_result_string = ''
    match_count = 0
    best_match_count = 0

    sentence_words = sentence.split()

    for string in sentence_words:
        result_string = (result_string + ' ' + string).strip()
        if result_string in text:
            match_count += 1
            if match_count > best_match_count:
                best_result_string = result_string
                best_match_count = match_count
        else:
            match_count = 0
            result_string = ''

    # Due to the fact that this is a clause locator (i.e. not word locator), individual word matches have been recognised in the same way as a complete match fail.
    # Otherwise words like 'for', will return a positive result.
    if best_match_count > 1:
        start_index = text.index(best_result_string)
        end_index = start_index + len(best_result_string) - 1
        return {"sentence": sentence , "text": text, "result_found": True, "start_index": start_index, "end_index": end_index, "resulting_match": best_result_string}

    else:
        return {"sentence": sentence ,"text": text, "result_found": False}


"""The app initialistion and routing takes place here. The API is very simple and only requires one routing option."""
APP = Flask("clause-locator")
    
@APP.route('/contract-query', methods=['POST'])
def solutions():
    # I have assigned request_obj here rather than in the input validation function becuase it allows me to
    # access the flask request easier(more readable). Furtheremore, this step does not required explicit validation since it is already handled
    # well.
    request_obj = request.json

    message, error_present = input_validation(request_obj)


    if error_present:
        raise ExceptionMessage(message, status_code=400)
    
    sentence = request_obj['sentence']
    text = request_obj['text']
    
    result = evaluate_result(text, sentence)
    print(result)

    # whilst it does not appear to be needed, I have used the jsonify function to ensure we have complete control over the responses returned, in terms of correct headers etc.
    return jsonify(result) 
   


"""The below function allows flask to handle errors and return an appropriate response."""
@APP.errorhandler(ExceptionMessage)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



if __name__ == "__main__":
    
    APP.run(debug=True)
