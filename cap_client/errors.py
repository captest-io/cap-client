"""
Exceptions and errors used in the client
"""


class ClientError(Exception):

    def __init__(self, message):
        self.message = message


class ValidationError(Exception):

    def __init__(self, message):
        self.message = message

