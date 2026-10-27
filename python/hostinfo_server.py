"""Serve the machine's hostname and IP address over HTTP."""

import argparse
import signal
import socket
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
	"""Handle HTTP GET requests with this host's name and IP address."""

	def do_GET(self):
		"""Return host information as a UTF-8 plain-text HTTP response."""
		body = get_host_info().encode("utf-8")
		self.send_response(200, "OK")
		self.send_header("Content-Type", "text/plain; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.end_headers()
		self.wfile.write(body)


def get_host_info():
	"""Return the system hostname and its resolved IP address, followed by newline."""
	hostname = socket.gethostname()
	return f"{hostname} {socket.gethostbyname(hostname)}\n"


def run_web_server(port):
	"""Serve host information on all interfaces until the process is stopped."""
	server_address = "0.0.0.0"
	started_at = datetime.now().astimezone().isoformat(timespec="seconds")
	print(f"Server listening on http://{server_address}:{port}, started on {started_at}")
	httpd = HTTPServer((server_address, port), SimpleHTTPRequestHandler)
	try:
		httpd.serve_forever()
	finally:
		httpd.server_close()


def terminate(_signum, _frame):
	"""Exit cleanly when the container runtime sends SIGTERM."""
	stopped_at = datetime.now().astimezone().isoformat(timespec="seconds")
	print(f"Termination requested at {stopped_at}, exiting...")
	sys.exit(0)


def main(argv=None):
	"""Parse the optional port, register SIGTERM handling, and start the server."""
	parser = argparse.ArgumentParser(description="Serve this host's name and IP address.")
	parser.add_argument(
		"port",
		default=9898,
		type=int,
		nargs="?",
		help="TCP port to listen on (default: 9898)",
	)
	args = parser.parse_args(argv)
	if not 1 <= args.port <= 65535:
		parser.error("port must be between 1 and 65535")
	signal.signal(signal.SIGTERM, terminate)
	run_web_server(args.port)


if __name__ == "__main__":
	main()