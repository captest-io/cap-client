"""
Exceptions and errors used in the client
"""


class ClientError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "ClientError: " + self.message


class ValidationError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "ValidationError: " + self.message

