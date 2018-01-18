from http.server import BaseHTTPRequestHandler, HTTPServer
import time, json, ssl
import subprocess
from subprocess import PIPE, STDOUT
import busstuff

hostName = ""
hostPort = 9000

'''''''''''''''''''''''
default response data
'''''''''''''''''''''''
defaultCard = {
  "content": "Lonestar program loaded successfully.",
  "title": "Lonestar",
  "type": "Simple"
}
defaultDirective = {
  "type": "AudioPlayer.Play",
  "playBehavior": "REPLACE_ALL",
  "audioItem": {
    "stream": {
      "token": "this-is-the-audio-token",
      "url": "https://s3.amazonaws.com/lonestarpi/sounds/input_ok_3_clean.mp3",
      "offsetInMilliseconds": 0
    }
  }
}
base_result = {
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "hello there from the internet!"
    },
    "shouldEndSession": False
  },
  "sessionAttributes": {}
}

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
  return ''
  #return subprocess.run(['ls', ''], stdout=subprocess.PIPE).stdout.decode('utf-8')

def playThaVideo():
  proc = subprocess.Popen(['omxplayer', '-o', 'hdmi', 'video.mp4'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)

def buildRes(text, cardContent="Lonestar program loaded successfully.", cardTitle="Lonestar"):
  print('build res: ' + text)
  result = {
    "version": "1.0",
    "response": {
      "directives": [
        {
          "type": "AudioPlayer.Play",
          "playBehavior": "REPLACE_ALL",
          "audioItem": {
            "stream": {
              "token": "this-is-the-audio-token",
              "url": "https://s3.amazonaws.com/lonestarpi/sounds/input_ok_3_clean.mp3",
              "offsetInMilliseconds": 0
            }
          }
        }
      ],
      "outputSpeech": {
        "type": "PlainText",
        "text": text
      },
      "card": {
        "content": "Lonestar program loaded successfully.",
        "title": "Lonestar BUS EDITION",
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

def buildPlaybackRes():
  result = {
    "version": "1.0",
    "response": {
      #"outputSpeech": {
        #"type": "PlainText",
        #"text": "playing the video!"
      #},
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
      "shouldEndSession": True,
      "directives": [
        {
          "type": "AudioPlayer.Play",
          "playBehavior": "REPLACE_ALL",
          "audioItem": {
            "stream": {
              "token": "this-is-the-audio-token",
              "url": "https://s3.amazonaws.com/lonestarpi/sounds/input_ok_3_clean.mp3",
              "offsetInMilliseconds": 0
            }
          }
        }
      ],
    },
    "sessionAttributes": {}
  }

  return result

class Result:
  def __init__(self, shouldEndSession=False, addChime=True):
    self.result = base_result

  def setText(self, text=''):
    speech = self.result['response']['ouputSpeech']
  
  def addCard(self, content='', title='', _type=''):
    card = self.result['response']['card'] = defaultCard
    if content:
      card['content'] = content
    if title:
      card['title'] = title
    if _type:
      card['type'] = _type

  def addChime(self):
    directives = self.result['response']['directives'] = []
    directives.append(defaultDirective)

  def addReprompt(self, text=''):
    reprompt = self.result['response']['reprompt'] = {}
    speech = reprompt['outputSpeech'] = {}
    speech['type'] = "PlainText"
    speech['text'] = text

  def setShouldEndSession(self, end=True):
    self.result['response']['shouldEndSession'] = end

  def getResult(self):
    return self.result


class Server(BaseHTTPRequestHandler):
  
  def parseRequest(self):
    i = self.body['request']['intent']['name']
    dh.INTENTS[i](self)

  def playMovieIntent(self):
    movie_input = self.body['request']['intent']['slots']['movie']['value']
    filename = MEDIA['movies'][movie_input]
    dh.data['proc'] = subprocess.Popen(['omxplayer', '-o', 'hdmi', filename], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    print('started movie')
    print('sending back buildPlaybackRes()')
    self.wfile.write(bytes(json.dumps(buildPlaybackRes()), "utf-8"))

  def pauseMovieIntent(self):
    if 'proc' not in dh.data:
      print('nothing playing')
      return
    outs, errs = dh.data['proc'].communicate(b' ')

  def playTVSeriesIntent(self):
    series_input = self.body['request']['intent']['slots']['object.name']['value']
    dh.playVideo(series_input)
    #series_input = self.body['request']['intent']['slots']['']
    res = Result()
    res.addChime()
    res.setShouldEndSession()
    res.addCard(content='playing show')
    self.wfile.write(bytes(json.dumps(res.getResult()), "utf-8"))

  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()

    nextBuses = {}
    #nextBuses['1'] = bus.newgetNextBus(('1', '3130'))
    for each in busstuff.tracking:
      #getNextBus returns (route_id, time, delay)
      nextBuses[each[0]] = bus.newgetNextBus(each)
      #busData.append(bus.getNextBus(each))

    speech = ""
    #print(nextBuses)
    for each in nextBuses:
      route_id = each
      print('route_id' + route_id)
      update = nextBuses[each][0]
      #print('update: ' + update)
      timeStr = update[0]
      trip_id = update[1]
      delay = update[2]
      mins = bus.timeUntil(timeStr).__str__()
      #timeStr = str(mins) + " minutes"
      speech += str("The next " + route_id + " bus arrives in " + mins + " minutes. ")
      speech += str('trip ' + trip_id + '.')
      if delay != '0':
        speech += str("With a delay value of " + delay + ". Whatever that means. ")

    self.wfile.write(bytes(json.dumps(buildRes(speech)), "utf-8"))
    #self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
    #self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
    #self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
    #self.wfile.write(bytes("</body></html>", "utf-8"))

  def do_POST(self):
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()

    content_len = int(self.headers['content-length'])
    #print(self.rfile.read(content_len).decode("utf-8"))
    self.body = json.loads((self.rfile.read(content_len)).decode("utf-8"))
    print(self.body)

    
    self.parseRequest()
    

    #self.wfile.write(bytes(json.dumps(buildRes()), "utf-8"))
    #result = dbstuff.getCarsAtDealership(body['index'])
    #result = list(result)
    #list(result)
    #self.wfile.write(bytes(str(result), "utf-8"))

class DataHandler():
  def __init__(self):
    print('constructor!')
    self.data = {}
    self.INTENTS = {
      'PlayMovie': Server.playMovieIntent,
      'AMAZON.PauseIntent': Server.pauseMovieIntent,
      'AMAZON.PlaybackAction<object@TVSeries>': Server.playTVSeriesIntent
    }

    FILE = 'media_files.json'
    with open(FILE) as json_file:
      self.media = json.load(json_file)

  def playVideo(self, value='', movie=False):
    if not value:
      return
    if not movie:
      filename = self.searchTV(value)
      #seach tv
    #search movies

    self.data['proc'] = subprocess.Popen(['omxplayer', '-o', 'hdmi', filename], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
      
  def searchTV(self, value=''):
    tv = self.media['tv']
    for show in tv:
      if value in show:
        s = tv[show]
        season, ep = s['current_ep'].split('.')
        return s['path'] + "Season " + season + "/" + s[season][ep]

bus = busstuff.Buses()
#bus.downloadTripUpdates()
#bus.getTripUpdates()

serv = HTTPServer((hostName, hostPort), Server)
#context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#context.load_cert_chain(certfile='./cert/cert.pem', keyfile='./cert/privkey.pem')
#serv.socket = context.wrap_socket(serv.socket, server_side=True)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

dh = DataHandler()

try:
  serv.serve_forever()
except KeyboardInterrupt:
  pass

serv.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))



