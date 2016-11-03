# Maria Karstens
# I downloaded a file from the OpenWeatherMap and it needed some editting:

import json

all_cities = open('cities.text','r') # all_cities is a string
# city_data is a list full of dictionaries that hold info about each town
l = all_cities.readlines()

for x in range(len(l)):
	l[x] = l[x].replace('\n','')
	l[x] = l[x] + ','
	l[x] = '{"_id"' + l[x][6:]

l[0] = "["+l[0]
l[-1] = l[-1][:-1] + "]"

f1 = "".join(l)

a = open('cities2.txt','w') # all_cities is a string

a.write(f1)
a.close()
all_cities.close()

b = open('cities2.txt','r')
fff = json.loads(b.read())
print fff[0]["_id"] # shows that my code worked

