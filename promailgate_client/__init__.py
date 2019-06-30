"""Proamilgate send API client"""

#  Copyright (C) Mike Norton, Matt Comben - All Rights Reserved
#  This file is part of ProMailGate.
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Matt Comben <matthew@dockstudios.co.uk>, 6/2019

from json import dumps
import requests

import promailgate_client.errors


class PromailgateClient(object):
    """Send client for Promailgate"""

    def __init__(
            self,
            host=None,
            url=None,
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None):
        """Setup variables"""
        self._host = host
        self._url = url
        self._use_ssl = use_ssl
        self._verify_ssl = verify_ssl
        self._default_api_key = default_api_key

    def _get_url(self):
        """Return the user-specified URL.
        Note: only works if user has supplied URL and not host"""
        return self._url

    def _get_host(self):
        """Return the user-specified host.
        Note: only works if user has supplied host and not URL"""
        return self._host

    def _get_proto(self):
        """Obtain protocol for connection
        Note: only works if user has supplied host and not URL"""
        return 'https' if self._use_ssl else 'http'

    def _get_base_url(self):
        """Return base URL of the endpoint"""
        if self._get_url():
            return self._get_url()
        return '%s://%s' % (self._get_proto(), self._get_host())

    def send_email(self, recipient, api_key=None, data=None, return_id=True):
        """Send an email using the API."""
        # Use empty dict, if no data is provided
        if data is None:
            data = {}

        if api_key is None:
            # Check that API key has either been provided in object creation or in this function
            if self._default_api_key is None:
                raise promailgate_client.errors.NoApiKeyProvidedError('No API key has been provided')

            # Set API key to default, if not provided in function
            api_key = self._default_api_key

        # Basic check to ensure that recipient is not an empty string
        if not recipient:
            raise promailgate_client.errors.NoRecipientProvidedError('No recipient has been provided')

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

        # Return successful
        if send_r.status_code == 201:
            # Return message ID if server provides this (based on return_id parameter)
            return send_r.json()['message_id']
        elif send_r.status_code == 200:
            # Otherwise, return True
            return True

        # Check for errors
        elif send_r.status_code == 401:
            # API key invalid
            raise promailgate_client.errors.InvalidAPIKeyError('Invalid API key')

        # Handle send error
        elif send_r.status_code == 400:
            error = 'No error provided'

            # If possible, obtain error from promailgate
            if 'Reason' in send_r.json():
                error = send_r.json()['Reason']

            # Otherwise, handle error from promailgate web server
            elif 'message' in send_r.json():
                error = send_r.json()['message']

            # Raise exception containing error
            raise promailgate_client.errors.SendError('Send error: %s' % error)

        elif send_r.status_code == 500:
            # Unknown server error
            raise promailgate_client.errors.UnknownSendError('Internal server error')

        else:
            # Raise exception when server return response code that isn't recognised
            raise promailgate_client.errors.UnknownResponseError('Unknown status code: %s' % send_r.status_code)

    def get_message_status(self, message_id):
        """Obtain status of sent message"""
        status_r = requests.get(
            '%s/api/message/status/%s' % (self._get_base_url(), message_id),
            headers={'Content-type': 'application/json'},
            verify=self._verify_ssl
        )

        # Return the JSON returned forom the server, if the result was successful.
        if status_r.status_code == 200:
            return status_r.json()

        # Handle errors from server
        # - message not found
        elif status_r.status_code == 404:
            raise promailgate_client.errors.NoSuchMessageError('No such message')

        # - internal server error
        elif status_r.status_code == 500:
            raise promailgate_client.errors.UnknownServerError('Unknown server error')

        # Handle case where server returns response code that we don't support
        else:
            raise promailgate_client.errors.UnknownResponseError('Unknown status code: %s' % status_r.status_code)
