#  Copyright (C) Mike Norton, Matt Comben - All Rights Reserved
#  This file is part of ProMailGate.
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Matt Comben <matthew@dockstudios.co.uk>, 6/2019

from unittest import mock, TestCase, skip

from promailgate_client import PromailgateClient
import promailgate_client.errors


class TestPromailgateClient(TestCase):
    """Test PromailgateClient class"""

    def test__get_url(self):
        """Test _get_url method"""
        client = PromailgateClient(
            host='test.endpoint.localhost',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)
        self.assertEqual(client._get_url(), None)

        client = PromailgateClient(
            url='http://test.localhost',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)
        self.assertEqual(client._get_url(), 'http://test.localhost')

    def test__get_base_url(self):
        """Test _get_base_url method"""
        # Test SSL connection
        client = PromailgateClient(
            host='test.endpoint.localhost',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        with mock.patch.object(client, '_get_proto', return_value='test_proto'):
            with mock.patch.object(client, '_get_host', return_value='test_hostname'):
                self.assertEqual(client._get_base_url(), 'test_proto://test_hostname')

        # Test SSL connection
        client = PromailgateClient(
            host='test.endpoint.localhost',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        with mock.patch.object(client, '_get_url', return_value='override://by.url.param'):
            self.assertEqual(client._get_base_url(), 'override://by.url.param')

    def test__get_host(self):
        """Test _get_host method"""
        client = PromailgateClient(
            host='TestHostnameHere',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_host(), 'TestHostnameHere')

    def test__get_proto(self):
        """Test _get_proto method"""
        # Test SSL connection
        client = PromailgateClient(
            host='Test',
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_proto(), 'https')

        # Test non-SSL connection
        client = PromailgateClient(
            host='Test',
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None)

        self.assertEqual(client._get_proto(), 'http')

    @skip('Not yet implemented')
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
        e500_message_id = 'this-raises-a-500'
        unknown_error_message_id = 'some-other-error'

        def mocked_requests_get(*args, **kwargs):
            if 'verify_ssl' in kwargs:
                verify_ssl = kwargs['verify_ssl']

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

            elif args[0] == 'https://%s/api/message/status/%s' % (test_hostname, e500_message_id):
                return MockResponse({}, 500)

            elif args[0] == 'https://%s/api/message/status/%s' % (test_hostname, unknown_error_message_id):
                return MockResponse({}, 123)

            else:
                raise Exception('Unknown endpoint')


        # Test http endpoint
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.get', side_effect=mocked_requests_get) as mocked_request:
            test_status = client.get_message_status(http_working_message_id)
            self.assertEqual(test_status, http_message_status)
            mocked_request.assert_called_once_with(
                'http://%s/api/message/status/%s' % (test_hostname, http_working_message_id),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Check SSL no-verify
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=True,
            verify_ssl=False,
            default_api_key=None
        )
        with mock.patch('requests.get', side_effect=mocked_requests_get) as mocked_request:
            test_status = client.get_message_status(https_working_message_id)
            self.assertEqual(test_status, https_message_status)
            mocked_request.assert_called_once_with(
                'https://%s/api/message/status/%s' % (test_hostname, https_working_message_id),
                headers={'Content-type': 'application/json'}, verify=False
            )

        client = PromailgateClient(
            host=test_hostname,
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None
        )

        with mock.patch('requests.get', side_effect=mocked_requests_get) as mocked_request:
            test_status = client.get_message_status(https_working_message_id)
            self.assertEqual(test_status, https_message_status)
            mocked_request.assert_called_once_with(
                'https://%s/api/message/status/%s' % (test_hostname, https_working_message_id),
                 headers={'Content-type': 'application/json'}, verify=True
            )

            # Check error cases
            #  - Unknown message
            with self.assertRaises(promailgate_client.errors.NoSuchMessageError):
                client.get_message_status(unknown_message_id )

            #  - Internal server error
            with self.assertRaises(promailgate_client.errors.UnknownServerError):
                client.get_message_status(e500_message_id)

            #  - Unhandled response code
            with self.assertRaises(promailgate_client.errors.UnknownResponseError):
                client.get_message_status(unknown_error_message_id)
