#  Copyright (C) Mike Norton, Matt Comben - All Rights Reserved
#  This file is part of ProMailGate.
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Matt Comben <matthew@dockstudios.co.uk>, 6/2019

class PromailgateClientException(Exception):
    """Base exception for client"""

    pass


class NoApiKeyProvidedError(PromailgateClientException):
    """No API key has been prodided"""

    pass


class NoRecipientProvidedError(PromailgateClientException):
    """No recipient has been provided for the email"""

    pass


class InvalidAPIKeyError(PromailgateClientException):
    """Invalid API key"""

    pass


class UnknownResponseError(PromailgateClientException):
    """Unknown status code returned by server"""

    pass


class SendError(PromailgateClientException):
    """Error during send"""

    pass


class UnknownSendError(PromailgateClientException):
    """Unknown server error during send"""

    pass


class NoSuchMessageError(PromailgateClientException):
    """No such message"""

    pass


class UnknownServerError(PromailgateClientException):
    """Unknown server error"""

    pass
