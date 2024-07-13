from rest_framework.exceptions import APIException

class SerializerInvalidException(APIException):
    status_code = 400
    default_detail = 'Invalid data provided.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = {'detail': self.default_detail}

        if code is not None:
            self.code = code
        else:
            self.code = self.default_code