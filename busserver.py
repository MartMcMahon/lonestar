from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import busstuff

hostName = ""
hostPort = 8080

bus = busstuff.Buses()

class Server(BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_POST(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		content_len = int(self.headers['content-length'])
		self.body = self.rfile.read(content_len).decode("utf-8")
		print(self.body)

serv = HTTPServer((hostName, hostPort), Server)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
try:
	serv.serve_forever()
except KeyboardInterrupt:
	pass

serv.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
		