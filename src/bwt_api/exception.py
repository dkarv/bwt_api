"""Exceptions for the BWT API."""


class BwtException(Exception):
    """General exception while accessing the api."""


class WrongCodeException(BwtException):
    """User code is wrong."""


class ApiException(BwtException):
    """Api Response status was not ok."""


class ConnectException(BwtException):
    """Connection issue."""
