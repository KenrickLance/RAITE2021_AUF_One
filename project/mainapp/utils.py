
from django.http import HttpResponse
import json

def make_http_response(response_status,response_message,response_data=None):
    data = []

    if response_data:
        data = [response_data]

    if response_status == 200:
        response = HttpResponse(
            json.dumps({
                'status': 'success',
                'message': response_message,
                'data': data
            }),
            content_type="application/json",
        )
        response.status_code = 200

    elif response_status == 400:
        response = HttpResponse(
            json.dumps({
                'status': 'error',
                'message': response_message,
                'data': data
            }),
            content_type="application/json",
        )
        response.status_code = 400
    
    return response

