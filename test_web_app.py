"""Optional automated tests for the local browser presentation interface."""

import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from unittest.mock import patch

import main
import web_app


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.original_file = main.DATA_FILE
        main.DATA_FILE = Path(cls.temp.name) / 'test_reports.json'
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), web_app.AppHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()
        main.DATA_FILE = cls.original_file
        cls.temp.cleanup()

    def setUp(self):
        if main.DATA_FILE.exists():
            main.DATA_FILE.unlink()

    def request(self, path='/', data=None):
        encoded = urlencode(data).encode('utf-8') if data is not None else None
        request = Request(self.base + path, encoded)
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read().decode('utf-8'), response.url
        except HTTPError as error:
            return error.code, error.read().decode('utf-8'), error.url

    def test_home_page_loads_without_reports(self):
        code, page, _ = self.request()
        self.assertEqual(code, 200)
        self.assertIn('Lost something?', page)
        self.assertIn('No reports yet.', page)

    def test_report_form_loads(self):
        code, page, _ = self.request('/new?type=found')
        self.assertEqual(code, 200)
        self.assertIn('Report A Found Item', page)
        self.assertIn('Campus location', page)

    def test_adding_report_saves_data(self):
        code, page, location = self.request('/new', {
            'type': 'lost', 'category': 'Bag', 'colour': 'black',
            'location': 'Fisher Library', 'description': 'small zip bag'
        })
        self.assertEqual(code, 200)  # follows 303 to match page
        self.assertTrue(location.endswith('/match?id=1'))
        self.assertIn('Possible matches for report #1', page)
        self.assertEqual(len(main.load_reports()), 1)

    def test_match_view_uses_same_core_algorithm(self):
        lost = main.ItemReport(1, 'lost', 'Bottle', 'Black', 'Fisher Library', 'silver lid metal')
        found = main.ItemReport(2, 'found', 'Bottle', 'Black', 'Fisher Library', 'silver lid metal')
        main.save_reports([lost, found])
        code, page, _ = self.request('/match?id=1')
        self.assertEqual(code, 200)
        self.assertIn('100', page)
        self.assertIn('Same colour (+25)', page)

    def test_resolve_updates_file(self):
        lost = main.ItemReport(1, 'lost', 'Bottle', 'Black', 'Fisher Library', 'metal')
        main.save_reports([lost])
        self.request('/resolve', {'id': '1'})
        self.assertEqual(main.load_reports()[0].status, 'resolved')

    def test_invalid_form_is_rejected(self):
        code, page, _ = self.request('/new', {'type': 'lost', 'category': 'Bottle',
                                            'colour': '', 'location': 'Library',
                                            'description': 'item'})
        self.assertEqual(code, 400)
        self.assertIn('Please complete all fields', page)
        self.assertEqual(main.load_reports(), [])

    def test_user_input_is_escaped(self):
        item = main.ItemReport(1, 'lost', 'Bag', 'Black', 'Library', '<script>alert(1)</script>')
        main.save_reports([item])
        code, page, _ = self.request('/')
        self.assertEqual(code, 200)
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)

    def test_missing_report_does_not_crash(self):
        code, page, _ = self.request('/match?id=999')
        self.assertEqual(code, 200)
        self.assertIn('requested active report was not found', page)

    def test_not_found_page_is_404(self):
        code, page, _ = self.request('/does-not-exist')
        self.assertEqual(code, 404)


if __name__ == '__main__':
    unittest.main()
