# webapp/errors.py
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from marshmallow import ValidationError

def error_response(status_code, message=None, details=None):
    payload = {
        'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'status': status_code
    }
    if message:
        payload['message'] = message
    if details:
        payload['details'] = details
    response = jsonify(payload)
    response.status_code = status_code
    return response

def handle_validation_error(error):
    if isinstance(error, ValidationError):
        return error_response(400, 'Validation failed', error.messages)
    return error_response(400, 'Invalid request parameters')

def handle_http_error(status_code):
    def handler(error):
        message = HTTP_STATUS_CODES.get(status_code, 'Unknown error')
        return error_response(status_code, message)
    return handler

def handle_db_error(error):
    return error_response(500, 'Database operation failed')

def handle_concurrent_update(error):
    return error_response(409, 'Resource version conflict')