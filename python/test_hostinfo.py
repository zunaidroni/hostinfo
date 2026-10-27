"""Offline unit tests for the hostinfo_server module."""

import signal
import sys
import unittest
from io import BytesIO, StringIO
from unittest.mock import patch

import hostinfo_server


class TestHostInfoServer(unittest.TestCase):
	"""Verify host lookup, HTTP response, shutdown, and startup behavior."""

	@patch("hostinfo_server.socket.gethostname", return_value="testhost")
	@patch("hostinfo_server.socket.gethostbyname", return_value="192.168.1.1")
	def test_get_host_info(self, mock_gethostbyname, mock_gethostname):
		self.assertEqual(hostinfo_server.get_host_info(), "testhost 192.168.1.1\n")
		mock_gethostname.assert_called_once_with()
		mock_gethostbyname.assert_called_once_with("testhost")

	@patch("hostinfo_server.get_host_info", return_value="testhost 192.168.1.1\n")
	def test_do_get_returns_host_info(self, _mock_get_host_info):
		response_buffer = BytesIO()

		class TestHandler(hostinfo_server.SimpleHTTPRequestHandler):
			"""Capture HTTP response writes without opening a network socket."""

			def __init__(self):
				self.wfile = response_buffer
				self.responses = []
				self.headers_sent = False

			def send_response(self, code, message=None):
				self.responses.append((code, message))

			def send_header(self, keyword, value):
				self.responses.append((keyword, value))

			def end_headers(self):
				self.headers_sent = True

		handler = TestHandler()
		handler.do_GET()

		self.assertEqual(handler.responses[0], (200, "OK"))
		self.assertIn(("Content-Type", "text/plain; charset=utf-8"), handler.responses)
		self.assertTrue(handler.headers_sent)
		self.assertEqual(response_buffer.getvalue(), b"testhost 192.168.1.1\n")

	def test_terminate_exits_successfully(self):
		captured_output = StringIO()
		with patch("hostinfo_server.sys.stdout", captured_output), patch("hostinfo_server.sys.exit") as mock_exit:
			hostinfo_server.terminate(None, None)
		mock_exit.assert_called_once_with(0)
		self.assertIn("Termination requested", captured_output.getvalue())

	@patch("hostinfo_server.signal.signal")
	@patch("hostinfo_server.run_web_server")
	def test_main_starts_server_on_requested_port(self, mock_run_web_server, mock_signal):
		with patch.object(sys, "argv", ["hostinfo_server.py", "8080"]):
			hostinfo_server.main()
		mock_signal.assert_called_once_with(signal.SIGTERM, hostinfo_server.terminate)
		mock_run_web_server.assert_called_once_with(8080)

	@patch("hostinfo_server.signal.signal")
	@patch("hostinfo_server.run_web_server")
	def test_main_uses_default_port(self, mock_run_web_server, mock_signal):
		with patch.object(sys, "argv", ["hostinfo_server.py"]):
			hostinfo_server.main()
		mock_signal.assert_called_once_with(signal.SIGTERM, hostinfo_server.terminate)
		mock_run_web_server.assert_called_once_with(9898)

	@patch("hostinfo_server.signal.signal")
	@patch("hostinfo_server.run_web_server")
	def test_main_rejects_invalid_port(self, mock_run_web_server, mock_signal):
		with patch.object(sys, "argv", ["hostinfo_server.py", "70000"]), patch("sys.stderr", new_callable=StringIO), self.assertRaises(SystemExit) as raised:
			hostinfo_server.main()
		self.assertEqual(raised.exception.code, 2)
		mock_signal.assert_not_called()
		mock_run_web_server.assert_not_called()

	@patch("hostinfo_server.HTTPServer")
	def test_run_web_server_closes_server_after_serving(self, mock_server_class):
		with patch("builtins.print"):
			hostinfo_server.run_web_server(8080)
		server = mock_server_class.return_value
		mock_server_class.assert_called_once_with(("0.0.0.0", 8080), hostinfo_server.SimpleHTTPRequestHandler)
		server.serve_forever.assert_called_once_with()
		server.server_close.assert_called_once_with()


if __name__ == "__main__":
	unittest.main(verbosity=2)
