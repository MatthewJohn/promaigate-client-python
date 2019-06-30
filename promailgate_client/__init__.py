# Copyright (C) Mike Norton, Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Matt Comben <matthew@dockstudios.co.uk>, June 2019

from json import dumps
import requests

from promailgate_client.errors import *


class PromailgateClient(object):

    def __init__(
            self, promailgate_host,
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None):
        """Setup variables"""
        self._promailgate_host = promailgate_host
        self._use_ssl = use_ssl
        self._verify_ssl = verify_ssl
        self._default_api_key = default_api_key

    def _get_proto(self):
        """Obtain protocol for connection"""
        return 'https' if self._use_ssl else 'http'

    def _get_base_url(self):
        """Return base URL of the endpoint"""
        return '%s://%s' % (self._get_proto(), self._promailgate_host)

    def send_email(self, recipient, api_key=None, data=None, return_id=True):
        """Send an email using the API."""
        # Use empty dict, if no data is provided
        if data is None:
            data = {}

        if api_key is None:
            # Check that API key has either been provided in object creation or in this function
            if self._default_api_key is None:
                raise NoApiKeyProvidedError('No API key has been provided')

            # Set API key to default, if not provided in function
            api_key = self._default_api_key

        # Basic check to ensure that recipient is not an empty string
        if not recipient:
            raise NoRecipientProvidedError('No recipient has been provided')

        # Send email
        send_r = requests.post(
            '%s/api/message/send' % self._get_base_url(),
            headers={'Content-type': 'application/json'},
            data=dumps({
                'api_key': api_key,
                'recipient': recipient,
                'data': data,
                'return_id': return_id
            }),
            verify=self._verify_ssl
        )

        # Check for errors
        if send_r.status_code == 401:
            # API key invalid
            raise InvalidAPIKeyError('Invalid API key')
        elif send_r.status_code == 400:
            # Send Error
            raise SendError('Send error: %s' % send_r.json()['Reason'])
        elif send_r.status_code == 500:
            # Unknown server error
            raise UnknownSendError('Server error: %s' % send_r.json()['Reason'])

        if send_r.status_code == 201:
            return send_r.json()['message_id']
        elif send_r.status_code == 200:
            return True
        else:
            raise UnknownResponseError('Unknown status code: %s' % send_r.status_code)

    def get_message_status(self, message_id):
        """Obtain status of sent message"""
        status_r = requests.get(
            '%s/api/message/status/%s' % (self._get_base_url(), message_id),
            headers={'Content-type': 'application/json'},
            verify=self._verify_ssl
        )

        if status_r.status_code == 404:
            raise NoSuchMessageError('No such message')

        elif status_r.status_code == 500:
            raise UnknownServerError('Unknown server error')

        elif status_r.status_code == 200:
            return status_r.json()

        else:
            raise UnknownResponseError('Unknown status code: %s' % status_r.status_code)
