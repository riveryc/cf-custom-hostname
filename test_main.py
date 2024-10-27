import unittest
from unittest import mock
import main

class TestMain(unittest.TestCase):

    @mock.patch('main.os.getenv')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='test_api_key')
    def test_get_api_key(self, mock_open, mock_getenv):
        # Test when environment variable is set
        mock_getenv.return_value = 'env_api_key'
        self.assertEqual(main.get_api_key(), 'env_api_key')

        # Test when environment variable is not set but file exists
        mock_getenv.return_value = None
        self.assertEqual(main.get_api_key(), 'test_api_key')

        # Test when neither environment variable is set nor file exists
        mock_open.side_effect = FileNotFoundError
        with self.assertRaises(Exception) as context:
            main.get_api_key()
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
        zone_ids = main.get_zone_ids(api_key)
        self.assertEqual(zone_ids, ['zone1', 'zone2'])

        # Test when request fails
        mock_response.status_code = 400
        with self.assertRaises(Exception) as context:
            main.get_zone_ids(api_key)
        self.assertTrue('Failed to retrieve zone IDs' in str(context.exception))

    @mock.patch('main.get_zone_ids')
    @mock.patch('main.get_api_key')
    def test_main(self, mock_get_api_key, mock_get_zone_ids):
        mock_get_api_key.return_value = 'test_api_key'
        mock_get_zone_ids.return_value = ['zone1', 'zone2']

        with mock.patch('builtins.print') as mock_print:
            main.main()
            mock_print.assert_called_with('Zone IDs:', ['zone1', 'zone2'])

if __name__ == '__main__':
    unittest.main()
