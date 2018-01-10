from pymongo import MongoClient
import json, datetime
import requests

tracking_route_ids = ("1", "7", "5", "801")
tracking_stop_ids = ("487", "1171", "982", "5405")
#(route_id, stop_id)
tracking = [
  ("801", "5405"),
  #("1", "487"),
  ("5", "982"),
  ("7", "1171")
]

class Buses:
  def __init__(self):
    db = MongoClient().bus_data
    self.collection = db.trips

  def getTripWithId(self, tripId):
    return self.collection.find_one({'_id': tripId})

  def pushTrip(self, trip):
    self.collection.save(trip)

  def getTripData(self):
    with open('trips.txt') as file:
      trip_data = file.read()

    trip_data = trip_data.split('\n')
    keys = trip_data[0].split(',')
    
    #last line is blank, so only use [:-1]
    for line in trip_data[:-1]:
      trip = dict()
      values = line.split(',')
      for index in range(0, len(values)):
        trip[keys[index]] = values[index]
      #push trip to db
      if trip['route_id'] in tracking_route_ids:
        trip['_id'] = trip['trip_id']
        self.pushTrip(trip)
        #print(trip)

  '''
  def pushTripToJson(self, trip):
    data = getTripDataFromJson()
    data[]
    with open('trips.json')
  '''

  def getTripsFromJson(self):
    with open('trips.json', 'r') as file:
      trips = file.read()
    return trips      

  def downloadTripUpdates(self):
    r = requests.get("https://data.texas.gov/download/mqtr-wwpy/text%2Fplain")
    FILE = 'bus_data.json'
    with open(FILE, 'w+') as file:
      file.write(r.text)

  def getTripUpdates(self):
    with open('bus_data.json', 'r') as file:
      data = json.loads(file.read())
    header = data['header']
    timestamp = header['timestamp']

    self.updates = data['entity']
    for update in self.updates:
      trip_id = update['trip_update']['trip']['trip_id']
      trip = self.collection.find_one({'_id':trip_id})
      if not trip:
        continue
      stuff = update['trip_update']['stop_time_update']
      vehicle = update['trip_update']['vehicle']

      if 'updates' not in trip:
        trip['updates'] = dict()

      for each in stuff:
        trip['updates'][each['stop_id']] = each

      trip['vehicle'] = vehicle
      
      self.pushTrip(trip)




  def getStopTimesFromTxt(self):
    with open('stop_times.txt') as file:
      stop_times = file.read()

    stop_times = stop_times.split('\n')
    keys = stop_times[0].split(',')

    data = dict()
    #last line is blank and first line is keys
    for line in stop_times[1:-1]:
      values = line.split(',')
      lineObj = dict()
      for index in range(0, len(values)):
        lineObj[keys[index]] = values[index]
      
      trip_id = lineObj['trip_id']
      if trip_id not in data:
        data[trip_id] = dict()
      
      stop_id = lineObj['stop_id']
      data[trip_id][stop_id] = lineObj['departure_time']

    #print(data)
    #go through what we extracted from the file, and save times for relavant trips
    for t in data:
      trip = self.collection.find_one({'_id':t})
      if not trip:
        continue
      trip['stops'] = data[t]
      self.pushTrip(trip)

  def getNextBus(self, data=("7", "1171")):
    print('bus ' + data[0])
    print('stop_id ' + data[1])
    times = []
    trips = self.collection.find({'route_id':data[0]})
    '''
    not sure about this if 'stops' if
    '''
    trip_ids = []
    for trip in trips:
      if 'stops' not in trip:
        continue
      stops = trip['stops']
      if data[1] in stops:
        times.append(stops[data[1]])
        trip_ids.append(trip['trip_id'])
        #print('trip_id: ' + trip['trip_id'])
    
    times.sort()
    #now = " 8:42:00"
    now = datetime.datetime.now()
    now_s = now.__str__()

    #format time string
    hour = self.formatHour(str(now.hour))
    minute = now.minute
    second = now.second
    now_s = hour + ':' + str(minute) + ':' + str(second)

    #find next bus
    lastBus = ''
    nextBus = ''
    for index in range(0, len(times))[::-1]:
      if now_s < times[index]:
        nextBus = times[index]
        print('trip: ' + trip_ids[index])
      else:
        lastBus = times[index]
        break

    #do time math
    nextBus_t = self.timeFromStr(nextBus)
    t = datetime.datetime.combine(datetime.datetime.today(), nextBus_t)
    delta = t + datetime.timedelta(hours=-now.hour, minutes=-now.minute, seconds=-now.second)
    
    print('delta: ' + delta.__str__())

    


    print('last bus: ' + lastBus)
    print('next bus: ' + nextBus)

    return (data[0], nextBus, delta)

  def timeFromStr(self, s):
    h, m, sec = s.split(':')
    h = int(h)
    m = int(m)
    sec = int(sec)
    return datetime.time(hour=h, minute=m, second=sec)

  def formatHour(self, hour):
    if hour < "03":
      hour = str(int(hour) + 24)
    elif hour < "10":
      hour = ' ' + hour[1]
    return hour
    


'''
FILE = 'bus_data.json'
with open(FILE) as file:
  data = json.load(file)

data = data['entity']
for e in data:
  update = dict()
  update['id'] = e['id']
  update['route'] = e['trip_update']['trip']['route_id']
  print(update)
'''

buses = Buses()
#buses.getTripData()
buses.downloadTripUpdates()
#buses.getTripData()
buses.getTripUpdates()
#buses.getStopTimesFromTxt()
#buses.getNextSeven()

busData = {}
for each in tracking:
  buses.getNextBus(each)