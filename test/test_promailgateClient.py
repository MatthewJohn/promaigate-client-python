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

    def test_send_email(self):
        """Test get_message_status"""

        test_hostname = 'sendemail.local.host'
        test_valid_api_key_1 = '1234567890'
        test_valid_api_key_2 = '0987654321'
        test_valid_api_key_3 = 'asdfghjkl'
        test_recipient_1 = 'alice@example.com'
        test_recipient_2 = 'bob@examples.co.uk'
        test_message_data_1 = {
            'first_name': 'Bob',
            'surname': 'Smith',
            'language': 'Promailgatish'
        }
        test_message_id = 'test-message-ide-here-1234556'

        def mocked_requests_post(*args, **kwargs):
            if 'verify_ssl' in kwargs:
                verify_ssl = kwargs['verify_ssl']

            class MockResponse:
                def __init__(self, json_data, status_code):
                    self.json_data = json_data
                    self.status_code = status_code

                def json(self):
                    return self.json_data

            # Ensure required arguments are present
            self.assertTrue('data' in kwargs)
            self.assertTrue('return_id' in kwargs['data'])
            self.assertTrue('recipient' in kwargs['data'])
            self.assertTrue('api_key' in kwargs['data'])

            if args[0] in ['http://%s/api/message/send' % test_hostname,
                           'https://%s/api/message/send' % test_hostname,
                           'http://test-endpoint:1534/api/message/send']:
                print(kwargs['data'])
                if kwargs['data']['return_id']:
                    return MockResponse({'Status': 'OK', 'message_id': test_message_id}, 201)
                else:
                    return MockResponse({'Status': 'OK'}, 200)

            else:
                raise Exception('Unknown endpoint')

        # Test http endpoint
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=False,
                                       data={}, api_key=test_valid_api_key_1)
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'http://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_1, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Test https endpoint
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=False,
                                       data={}, api_key=test_valid_api_key_1)
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'https://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_1, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Test with SSL no verify
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=True,
            verify_ssl=False,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_2, return_id=False,
                                       data={}, api_key=test_valid_api_key_2)
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'https://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_2, test_recipient_2
                ),
                headers={'Content-type': 'application/json'}, verify=False
            )

        # Test with default API key
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=test_valid_api_key_3
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=False,
                                       data={})
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'http://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_3, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Test with default and send-specific API key
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=test_valid_api_key_2
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=False,
                                       data={}, api_key=test_valid_api_key_2)
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'http://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_2, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Test with URL
        client = PromailgateClient(
            url='http://test-endpoint:1534',
            use_ssl=False,
            verify_ssl=True,
            default_api_key=test_valid_api_key_2
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=False,
                                       data={}, api_key=test_valid_api_key_2)
            self.assertEqual(send_r, True)
            mocked_request.assert_called_once_with(
                'http://test-endpoint:1534/api/message/send',
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": false}' % (
                    test_valid_api_key_2, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )

        # Test return ID
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=True,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            send_r = client.send_email(recipient=test_recipient_1, return_id=True,
                                       data={}, api_key=test_valid_api_key_1)
            self.assertEqual(send_r, test_message_id)
            mocked_request.assert_called_once_with(
                'https://%s/api/message/send' % test_hostname,
                data='{"api_key": "%s", "recipient": "%s", "data": {}, "return_id": true}' % (
                    test_valid_api_key_1, test_recipient_1
                ),
                headers={'Content-type': 'application/json'}, verify=True
            )


        # Test with send error

        # Test with internal server error

        # Test with unknown response code

        # Test with data

        #
        # # Check SSL no-verify
        # client = PromailgateClient(
        #     host=test_hostname,
        #     use_ssl=True,
        #     verify_ssl=False,
        #     default_api_key=None
        # )
        # with mock.patch('requests.get', side_effect=mocked_requests_get) as mocked_request:
        #     test_status = client.get_message_status(https_working_message_id)
        #     self.assertEqual(test_status, https_message_status)
        #     mocked_request.assert_called_once_with(
        #         'https://%s/api/message/status/%s' % (test_hostname, https_working_message_id),
        #         headers={'Content-type': 'application/json'}, verify=False
        #     )


        # Test no API key provided
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            with self.assertRaises(promailgate_client.errors.NoApiKeyProvidedError):
                client.send_email(recipient=test_recipient_1, return_id=False, data={})

            # Ensure that API wal not called
            mocked_request.assert_not_called()

        # Test no recipient provided
        client = PromailgateClient(
            host=test_hostname,
            use_ssl=False,
            verify_ssl=True,
            default_api_key=None
        )
        with mock.patch('requests.post', side_effect=mocked_requests_post) as mocked_request:
            with self.assertRaises(promailgate_client.errors.NoRecipientProvidedError):
                client.send_email(recipient='', api_key=test_valid_api_key_1, return_id=False, data={})

            # Ensure that API wal not called
            mocked_request.assert_not_called()


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

        # Check HTTPS endpoint
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

        with mock.patch('requests.get', side_effect=mocked_requests_get) as mocked_request:
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
