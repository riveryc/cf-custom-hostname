import unittest
from unittest import mock
import main

class TestMain(unittest.TestCase):

    @mock.patch('main.os.getenv')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='test_api_key')
    def test_get_cred(self, mock_open, mock_getenv):
        # Test when environment variables are set
        mock_getenv.side_effect = ['env_api_key', 'env_auth_email']
        self.assertEqual(main.get_cred(), ('env_api_key', 'env_auth_email'))

        # Test when environment variables are not set but files exist
        mock_getenv.side_effect = [None, None]
        self.assertEqual(main.get_cred(), ('test_api_key', 'test_api_key'))

        # Test when neither environment variables are set nor files exist
        mock_open.side_effect = FileNotFoundError
        with self.assertRaises(Exception) as context:
            main.get_cred()
        self.assertTrue('API key not found' in str(context.exception))

    @mock.patch('main.requests.get')
    def test_get_zone_ids(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [{'id': 'zone1'}, {'id': 'zone2'}]
        }
        mock_get.return_value = mock_response

        api_key = 'test_api_key'
        auth_email = 'test_auth_email'
        zone_ids = main.get_zone_ids(api_key, auth_email)
        self.assertEqual(zone_ids, ['zone1', 'zone2'])

        # Test when request fails
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "errors": [{"code": 6111, "message": "Invalid format for Authorization header"}],
            "messages": [],
            "result": None
        }
        with self.assertRaises(Exception) as context:
            main.get_zone_ids(api_key, auth_email)
        self.assertTrue('Invalid format for Authorization header' in str(context.exception))

        # Test when request fails with other error
        mock_response.json.return_value = {
            "success": False,
            "errors": [{"code": 1234, "message": "Some other error"}],
            "messages": [],
            "result": None
        }
        with self.assertRaises(Exception) as context:
            main.get_zone_ids(api_key, auth_email)
        self.assertTrue('Failed to retrieve zone IDs' in str(context.exception))

    @mock.patch('main.get_zone_ids')
    @mock.patch('main.get_cred')
    def test_main(self, mock_get_cred, mock_get_zone_ids):
        mock_get_cred.return_value = ('test_api_key', 'test_auth_email')
        mock_get_zone_ids.return_value = ['zone1', 'zone2']

        with mock.patch('builtins.print') as mock_print:
            main.main()
            mock_print.assert_called_with('Zone IDs:', ['zone1', 'zone2'])

    @mock.patch('main.dns.resolver.Resolver.resolve')
    def test_verify_acme_challenge(self, mock_resolve):
        mock_resolve.return_value = ['"test_challenge"']
        with mock.patch('builtins.print') as mock_print:
            main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('ACME challenge for example.com: "test_challenge"')

        mock_resolve.side_effect = main.dns.resolver.NoAnswer
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('No ACME challenge found for example.com. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        mock_resolve.side_effect = main.dns.resolver.NXDOMAIN
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('Hostname example.com does not exist. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        mock_resolve.side_effect = Exception('Test error')
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('Error verifying ACME challenge for example.com: Test error. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        # Test CNAME verification
        mock_resolve.return_value = ['cname.example.com']
        with mock.patch('builtins.print') as mock_print:
            main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('CNAME for _acme-challenge.example.com: cname.example.com')

        mock_resolve.side_effect = main.dns.resolver.NoAnswer
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('No CNAME found for _acme-challenge.example.com. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        mock_resolve.side_effect = main.dns.resolver.NXDOMAIN
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('Hostname _acme-challenge.example.com does not exist. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        mock_resolve.side_effect = Exception('Test error')
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('Error verifying CNAME for _acme-challenge.example.com: Test error. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

        # Test combined TXT and CNAME verification
        mock_resolve.side_effect = [main.dns.resolver.NoAnswer, ['cname.example.com']]
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('No ACME challenge found for example.com. Current record: None, Desired record: _acme-challenge.example.com')
            mock_print.assert_called_with('CNAME for _acme-challenge.example.com: cname.example.com')
            self.assertTrue(result)

        mock_resolve.side_effect = [['"test_challenge"'], main.dns.resolver.NoAnswer]
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('ACME challenge for example.com: "test_challenge"')
            mock_print.assert_called_with('No CNAME found for _acme-challenge.example.com. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertTrue(result)

        mock_resolve.side_effect = [main.dns.resolver.NoAnswer, main.dns.resolver.NoAnswer]
        with mock.patch('builtins.print') as mock_print:
            result = main.verify_acme_challenge('example.com')
            mock_print.assert_called_with('No ACME challenge found for example.com. Current record: None, Desired record: _acme-challenge.example.com')
            mock_print.assert_called_with('No CNAME found for _acme-challenge.example.com. Current record: None, Desired record: _acme-challenge.example.com')
            self.assertFalse(result)

    @mock.patch('main.verify_acme_challenge')
    @mock.patch('main.get_zone_ids')
    @mock.patch('main.get_cred')
    def test_main_with_hostname(self, mock_get_cred, mock_get_zone_ids, mock_verify_acme_challenge):
        mock_get_cred.return_value = ('test_api_key', 'test_auth_email')
        mock_get_zone_ids.return_value = ['zone1', 'zone2']

        test_args = ['main.py', '--hostname', 'example.com']
        with mock.patch('sys.argv', test_args):
            main.main()
            mock_verify_acme_challenge.assert_called_with('example.com')

    @mock.patch('main.dns.resolver.Resolver.resolve')
    def test_is_valid_cname_target(self, mock_resolve):
        mock_resolve.return_value = ['192.0.2.1']
        self.assertTrue(main.is_valid_cname_target('cname.example.com'))

        mock_resolve.side_effect = Exception('Test error')
        self.assertFalse(main.is_valid_cname_target('cname.example.com'))

    @mock.patch('builtins.input', side_effect=['yes'])
    def test_main_proceed_yes(self, mock_input):
        with mock.patch('builtins.print') as mock_print:
            main.main()
            mock_print.assert_any_call("All checks successful. Ready to implement custom hostname.")
            mock_print.assert_any_call("Exiting.")

    @mock.patch('builtins.input', side_effect=['no'])
    def test_main_proceed_no(self, mock_input):
        with mock.patch('builtins.print') as mock_print:
            main.main()
            mock_print.assert_any_call("All checks successful. Ready to implement custom hostname.")
            mock_print.assert_any_call("Exiting.")

if __name__ == '__main__':
    unittest.main()
