from rest_framework import status
from rest_framework.exceptions import APIException


class EmailAlreadyRegistered(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'A user with this email already exists.'
    default_code = 'email_already_registered'


class EmailNotVerified(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    # The code tells this 403 from the one for a request from another site
    default_detail = {
        'detail': 'Email is not verified.',
        'code': 'email_not_verified',
    }
    default_code = 'email_not_verified'
