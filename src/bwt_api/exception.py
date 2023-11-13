class BwtException(Exception):
    "General exception while accessing the api"
    pass

class WrongCodeException(BwtException):
    "User code is wrong"
    pass

class ApiException(BwtException):
    "Api Response status was not ok"
    pass

class ConnectException(BwtException):
    "Connection issue"
    pass
