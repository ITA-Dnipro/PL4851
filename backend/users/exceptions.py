from rest_framework import status
from rest_framework.exceptions import APIException


class EmailAlreadyRegistered(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A user with this email already exists.'
    default_code = 'email_already_registered'
