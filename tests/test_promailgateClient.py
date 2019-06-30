#  Copyright (C) Mike Norton, Matt Comben - All Rights Reserved
#  This file is part of ProMailGate.
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Matt Comben <matthew@dockstudios.co.uk>, 6/2019

import unittest
from unittest import mock, TestCase
from unittest import TestCase

import requests

from promailgate_client import PromailgateClient
from promailgate_client.errors import *


class TestPromailgateClient(TestCase):
    """Test PromailgateClient class"""

    def test__get_base_url(self):
        """Test _get_base_url method"""
        # Test SSL connection
        client = PromailgateClient(
            promailgate_host='test.endpoint.localhost',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        with mock.patch.object(client, '_get_proto', return_value='test_proto'):
            with mock.patch.object(client, '_get_promailgate_host', return_value='test_hostname'):
                self.assertEqual(client._get_base_url(), 'test_proto://test_hostname')

    def test__get_promailgate_host(self):
        """Test _get_promailgate_host method"""
        client = PromailgateClient(
            promailgate_host='TestHostnameHere',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_promailgate_host(), 'TestHostnameHere')

    def test__get_proto(self):
        """Test _get_proto method"""
        # Test SSL connection
        client = PromailgateClient(
            promailgate_host='Test',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_proto(), 'https')

        # Test non-SSL connection
        client = PromailgateClient(
            promailgate_host='Test',
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_proto(), 'http')

    def test_send_email(self):
        self.fail()

    def test_get_message_status(self):
        """Test get_message_status"""

        test_hostname = 'testpromailgate.localhost'
        http_working_message_id = '123-test-456-message-id'
        http_message_status = {'MessageStatus': 'SENT', 'external_id': 'externalid-here-plz'}
        https_working_message_id = '654-https-message-id-here-123'
        https_message_status = {'MessageStatus': 'UNKNOWN_ERROR', 'external_id': 'another-external-id'}
        unknown_message_id = 'this-id-definitely-doesnt-exist'

        def mocked_requests_get(*args, **kwargs):
            class MockResponse:
                def __init__(self, json_data, status_code):
                    self.json_data = json_data
                    self.status_code = status_code

                def json(self):
                    return self.json_data

            if args[0] == 'http://%s/api/message/status/%s' % (test_hostname, http_working_message_id):
                return MockResponse(http_message_status, 200)

            elif args[0] == 'https://%s/api/message/status/%s' % (test_hostname, https_working_message_id):
                return MockResponse(https_message_status, 200)

            elif args[0] == 'https://%s/api/message/status/%s' % (test_hostname, unknown_message_id):
                return MockResponse({}, 404)

            else:
                raise Exception('Unknown endpoint')

            return MockResponse(None, 404)

        with mock.patch('requests.get', side_effect=mocked_requests_get):
            # Test http endpoint
            client = PromailgateClient(
                promailgate_host=test_hostname,
                use_ssl=False,
                verify_ssl=True,
                default_api_key=None
            )

            test_status = client.get_message_status(http_working_message_id)
            self.assertEqual(test_status, http_message_status)

            client = PromailgateClient(
                promailgate_host=test_hostname,
                use_ssl=True,
                verify_ssl=True,
                default_api_key=None
            )

            test_status = client.get_message_status(https_working_message_id)
            self.assertEqual(test_status, https_message_status)

            with self.assertRaises(NoSuchMessageError):
                client.get_message_status(unknown_message_id )
