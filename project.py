# SI 106 Final Project
# Maria Karstens
# April 17, 2016

import requests
import json
# import test
import math

# ====================================================================================================
# ========================================== Place() class ===========================================
# ====================================================================================================
class Place():
	base_url = "http://api.openweathermap.org/data/2.5/forecast"
	api_key = "a3763d8d77b508b1c0d9263874ab5754"
	air_density = 1.225 # units kg/m^3
	swept_area = 1 # units m^2
	cp = 16.0/27 # betz limit
	b_voltage = 0.68
	solar_panel_voltage = 20
	initial_current = math.pow(10,-11)
	k = 8.62*math.pow(10,-5)

	def __init__(self,idd):
		self.id = idd

	def get_info(self):
		self.url_parameters = {"id": self.id, "APPID": self.api_key}
		# requesting information from the internet:
		self.weather_dic = requests.get(self.base_url, params = self.url_parameters).json()
		
		# opening file to write in it:
		f = open("data_{}.txt".format(str(self.id)) , 'w')
		f.write(json.dumps(self.weather_dic))
		f.close()

		# opening file to read content:
		data = open("data_{}.txt".format(str(self.id)), 'r')
		self.data_list = json.loads(data.read())
		data.close()

	def calculate_power(self, w_condition, w = 0, s = 0, T = 0):
		if w_condition == True:
			velocity = w
			return 0.5*self.air_density*self.swept_area*(velocity**3)*self.cp
		else:
			if s <= 40:
				efficiency = s/100*3/2
			elif s > 40 & s <= 50:
				efficiency = (s+20)/100
			elif s > 50 & s <= 55:
				efficiency = 0.75
			elif s > 55 & s <= 80:
				efficiency = 0.80
			else:
				efficiency = s/100
			total_current = self.initial_current*math.exp(self.b_voltage/self.k/T - 1)
			return efficiency*self.solar_panel_voltage*total_current

	def total_power(self):
		self.power_per_day = {}
		for k in self.info:
			if k["date"] not in self.power_per_day:
				self.power_per_day[k["date"]] = {"WP": k["wind_power"],"SP": k["solar_power"]}
			else:
				self.power_per_day[k["date"]]["WP"] += k["wind_power"]
				self.power_per_day[k["date"]]["SP"] += k["solar_power"]

	def extract_info(self):
		self.name = str(self.data_list["city"]['name'])
		self.info = []
		# change cloudiness to sunlight percentage and account for the time of day
		for x in range(len(self.data_list["list"])):
			if ((int(self.data_list['list'][x]['dt_txt'][11:12]) == 0) & (int(self.data_list['list'][x]['dt_txt'][12:13]) < 5)) | (int(self.data_list['list'][x]['dt_txt'][11:13]) > 16):
				sunlight = 0
			else:
				sunlight = 100 - self.data_list['list'][x]["clouds"]['all']
			self.info.append({ "date": str(self.data_list['list'][x]['dt_txt'])[:10],
								"time": str(self.data_list['list'][x]['dt_txt'])[11:17],
								"wind": self.data_list['list'][x]["wind"]["speed"],
								"sun": sunlight,
								"temp": self.data_list['list'][x]["main"]["temp"]})
			self.info[x]["wind_power"] = self.calculate_power(True, w = self.info[x]["wind"])
			self.info[x]["solar_power"] = self.calculate_power(False, s = self.info[x]["sun"], T = self.info[x]["temp"])

# ====================================================================================================
# =============================== Function: Checking input from user =================================
# ====================================================================================================
def check_input_from_user(p):
	# Open cities.txt file to obtain id of all the cities the user entered:
	all_cities = open('cities.txt','r')
	city_data = json.loads(all_cities.read()) #city_data is a LIST full of dictionaries that hold info about each town
	all_cities.close()

	# check that all the cities are in API:
	places2 = [] # this list holds all the class Place instances
	p = [each.strip().lower() for each in p]
	for i in p:
		id_of_city = True
		position = 0
		while id_of_city:
			if position == len(city_data):
				print "------> Could not find city id number for city named {}. Will not include {} in the data.".format(i,i)
				id_of_city = False
			else:
				if city_data[position]['name'].lower() == i:
					id_of_city = False
					places2.append(Place(city_data[position]['_id']))
			position += 1
	return places2

# ====================================================================================================
# ======================================= Function: output csv =======================================
# ====================================================================================================
def output_csv(all_places):
	output_file = open("information.csv", 'w')
	try:
		for s in all_places:
			output_file.write("city:,{},\n, ,date, time, wind speed (m/s), wind power (W), sunlight (%),solar power (W)\n".format(s.name))
			for n in s.info:
				output_file.write(" , ,{},{},{},{},{},{}\n".format(n["date"],n["time"],("%.2f" % n["wind"]),("%.2f" % n["wind_power"]),n["sun"],("%.2f" % n["solar_power"])))
	except:
		print "Could not write {} into file".format(s.name)
.

# ====================================================================================================
# ======================================= Function: output csv =======================================
# ====================================================================================================
def output_data(all_places):
	print "\nBest days for Power Generation in..."
	for k in all_places:
		print "\n"+k.name + ":"
		for day in sorted(k.power_per_day, key = lambda x: k.power_per_day[x]["WP"] + k.power_per_day[x]["SP"], reverse = True):
			# '"%.2f" &' makes the float have two digits after the decimal
			print day+": "+("%.2f" % k.power_per_day[day]["WP"])+"W from wind\n"+ " "*12 +("%.2f" % k.power_per_day[day]["SP"])+"W from solar"

# ====================================================================================================
# ==================================== Obtain cities from user =======================================
# ===================1=================================================================================
places = []
state = True
print "This program will calculate the estimated power generated by a standard 20V solar panel and 1m^2 swept area wind turbine for the next six days for every city you enter."
print "The program will order the days by highest total power generated.\n"
while state:
	input = raw_input('Enter a city in the United States: ')
	if input.lower() == "done":
		state = False
	else:
		if input not in places:
			places.append(input)

places = check_input_from_user(places)

for x in places:
	x.get_info()
	x.extract_info()
	x.total_power()

output_csv(places)
output_data(places)

# ====================================================================================================
# ============================================ Test Cases ============================================
# # ====================================================================================================
# print "\n=============================== Test Cases ==============================="
# # Test 1: Testing that the invalid city names are taken out and the function check_input_from_user() returns only two class instances of Place.
# places_test1 = ["not_a_city","Flagler County","CHiCagO","also not a city"]
# test.testEqual(len(check_input_from_user(places_test1)),2,"Test 1")

# # Test 2:
# places_test2 = ["Flagler County","Orland Park","Radcliff","Orland Park"]
# check2 = check_input_from_user(places_test2)[2]
# test.testEqual(check2.id,4305504,"Test 2")

# # Test 3 & 4:
# check3 = check_input_from_user(places_test2)[2]
# test.testEqual(str(check3.calculate_power(True))[:3],"0.0","Test 3")
# test.testEqual(str(check3.calculate_power(True,w=1))[:6],"0.3629","Test 4")

# # Test 5:
# places_test5 = ["Drake"]
# check5 = check_input_from_user(places_test5)
# check5[0].get_info()
# test.testEqual(len(open("data_4464080.txt", 'r').readlines()),1,"Test 5")

# # Test 6 & 7 & 8 & 9:
# p6 = Place(4673179)
# test.testEqual(p6.id,4673179,"Test 6")
# p6.get_info()
# p6.extract_info()
# test.testEqual(p6.name,"Bee House","Test 7")
# test.testEqual(len(p6.info),40,"Test 8")
# test.testEqual(len(p6.info[0]),7,"Test 9")

# # Test 10:
# places_test10 = ["not a city"]
# check10 = check_input_from_user(places_test10)
# test.testEqual(len(check10),0,"Test 10")

