from http.server import BaseHTTPRequestHandler, HTTPServer
import time, json
from subprocess import call

hostName = ""
hostPort = 9000

sample_result = {
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "hello there from the internet!"
    },
    "card": {
      "content": "Lonestar program loaded successfully.",
      "title": "Lonestar LCARS",
      "type": "Simple"
    },
    "reprompt": {
      "outputSpeech": {
        "type": "PlainText",
        "text": ""
      }
    },
    "shouldEndSession": False
  },
  "sessionAttributes": {}
}

def ls():
  return call('ls')

def buildRes():
  result = {
    "version": "1.0",
    "response": {
      "outputSpeech": {
        "type": "PlainText",
        "text": ls()
      },
      "card": {
        "content": "Lonestar program loaded successfully.",
        "title": "Lonestar LCARS",
        "type": "Simple"
      },
      "reprompt": {
        "outputSpeech": {
          "type": "PlainText",
          "text": ""
        }
      },
      "shouldEndSession": True
    },
    "sessionAttributes": {}
  }

  return result


class Server(BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write(bytes(json.dumps(buildRes()), "utf-8"))
    #self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
    #self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
    #self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
    #self.wfile.write(bytes("</body></html>", "utf-8"))

  def do_POST(self):
    content_len = int(self.headers['content-length'])
    body = json.loads((self.rfile.read(content_len)).decode("utf-8"))
    print(body)

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    #result = dbstuff.getCarsAtDealership(body['index'])
    #result = list(result)
    #list(result)
    #self.wfile.write(bytes(str(result), "utf-8"))
    for car in result:
      self.wfile.write(bytes(json.dumps(car), "utf-8"))

serv = HTTPServer((hostName, hostPort), Server)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
  serv.serve_forever()
except KeyboardInterrupt:
  pass

serv.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))



