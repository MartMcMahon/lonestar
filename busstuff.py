from pymongo import MongoClient
import json, datetime
import requests

tracking_route_ids = ("1", "7", "5", "801")
tracking_stop_ids = ("487", "1171", "982", "5405")
#(route_id, stop_id)
tracking = [("801", "5405"), 
	#("1", "487"),	
	("5", "982"),	
	("7", "1171")
]

class Buses:
	def __init__(self):
		db = MongoClient().bus_data
		self.collection = db.trips
		self.busCol = db.buses
		self.updatesCol = db.updates

		#########
		#self.getTripData()
		#self.downloadTripUpdates()
		#self.getTripUpdates()

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
			delayObj = {}
			trip_id = update['trip_update']['trip']['trip_id']
			delayObj = {'trip_id':trip_id}
			trip = self.collection.find_one({'_id':trip_id})
			if not trip:
				continue
			#stuff = update['trip_update']['stop_time_update']
			trip_update = update['trip_update']
			vehicle = update['trip_update']['vehicle']

			t = trip_update['trip']

			for delay in trip_update['stop_time_update']:
				updateObj = {'trip_id': t['trip_id'],
					'start_time': t['start_time'],
					'start_date': t['start_date'],
					'route_id': t['route_id'],
					'timestamp': trip_update['timestamp']}

				if trip_update['vehicle']:
					updateObj['vehicle'] = trip_update['vehicle']

				if delay['departure']:
					updateObj['delay'] = delay['departure']['delay']
					updateObj['time'] = delay['departure']['time']
					updateObj['stop_id'] = delay['stop_id']

					#skip saving if this instance already exists
					if self.updatesCol.find_one({'timestamp': updateObj['timestamp'], 'route_id': updateObj['route_id'], 'stop_id': updateObj['stop_id']}):
						continue

					self.updatesCol.save(updateObj)

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

	def getBusDBObj(self, id=0, onTime=True):
		bus = {'_id': id}
		return bus

	def getDelay(self, trip_id, stop_id):
		#change to find_one once ur sure this is working right
		res = self.updatesCol.find({'trip_id': trip_id, 'stop_id': stop_id})

		if res.count() == 1:
			return res[0]
		elif res.count() == 0:
			return '0'
		else:
			# res has more than one result, so return only the one w/ highest timestamp
			timestamp = 0
			for update in res:
				if update['timestamp'] > timestamp:
					r = update
					timestamp = update['timestamp']

			return r

	def newgetNextBus(self, data=("7", "1171")):
		nextBuses = []
		route_id = data[0]
		stop_id = data[1]
		print('bus ' + route_id)
		print('stop_id' + stop_id)
		trips = self.collection.find({'route_id':route_id})

		for trip in trips:
			if 'stops' not in trip:
				continue
			stops = trip['stops']
			#make sure the stop is listed here
			if stop_id not in stops:
				continue
			#nextBus = {'route_id':route_id, 'stop_id':stop_id}
			#(time, trip_id)
			nextBuses.append((stops[stop_id], trip['trip_id']))

		#get now
		self.now = now = datetime.datetime.now()
		now_s = now.__str__()

		#format time string
		hour = now.hour
		minute = now.minute
		second = now.second
		now_s = str(hour) + ':' + str(minute) + ':' + str(second)

		#now_s = "19:00:00"

		nextBuses.sort()
		for c in range(0, len(nextBuses)):
			if now_s < nextBuses[c][0]:
				nextBuses = nextBuses[c:]
				break

		newNextBuses = []
		for bus in nextBuses:
			delay = self.getDelay(bus[1], stop_id)
			if not delay:
				delay = '0'
			update = (bus[0], bus[1], delay)
			newNextBuses.append(update)
		nextBuses = newNextBuses

		return nextBuses
	
	def timeUntil(self, time_s):
		now = self.now
		#get time obj from string
		time_t = self.timeFromStr(time_s)
		#get datetime obj with today for datetime math
		t = datetime.datetime.combine(datetime.datetime.today(), time_t)
		delta = t + datetime.timedelta(hours=-now.hour, minutes=-now.minute, seconds=-now.second)
		return delta.minute

	def timeFromStr(self, s):
		h, m, sec = s.split(':')
		h = int(h)
		if h > 23:
			h -= 24
		m = int(m)
		sec = int(sec)
		return datetime.time(hour=h, minute=m, second=sec)

	def formatHour(self, hour):
		if hour < "3":
			hour = str(int(hour) + 24)
		#elif hour < "10":
			#hour = ' ' + hour[1]
		return hour

if __name__ == "__main__":
	buses = Buses()
	#buses.getTripData()
	#buses.downloadTripUpdates()
	#buses.getTripData()
	#buses.getTripUpdates()
	buses.newgetNextBus()
	#buses.getStopTimesFromTxt()
	#buses.getNextSeven()

	busData = {}
	#for each in tracking:
		#buses.getNextBus(each)

