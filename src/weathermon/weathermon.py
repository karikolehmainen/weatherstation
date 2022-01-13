import psycopg2
import paho.mqtt.client as mqtt
from time import sleep
from datetime import datetime

CONNECTION = "postgres:postgres:password@localhost:5432/example"
PSQL_USER = "postgres"
PSQL_PASS = "password"
PSQL_HOST = "host"
MQTT_HOST = "0.0.0.0"
PSQL_DB = "example"
LOCATION = "test"

class WeatherStation:
	def __init__(self):
		self.api_key = "54321"
		self.client=mqtt.Client(self.api_key,False)
		self.client.on_message=self.on_message
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		ret = self.client.connect(MQTT_HOST,port=1883)
		if (ret == 0):
			self.client.subscribe("#")
			self.client.loop_start()

		# postgre
		self.conn = psycopg2.connect(host=PSQL_HOST, port="5432", user=PSQL_USER, password=PSQL_PASS, dbname=PSQL_DB)
		print("Weatherstation started: "+str(ret))

	def on_connect(self, client, userdata, flags, rc):
		print("on_connect: "+str(rc))
		if rc==0:
			print("connected OK Returned code=",rc)
		else:
			print("Bad connection Returned code=",rc)

	def on_disconnect(self,client, userdata, rc):
		if (rc != 0):
			print("Unexpected MQTT disconnection. Attempting to reconnect.")
		try:
			client.reconnect()
		except socket.error:
			print("reconnect socket error")

	def on_message(self,client, userdata, message):
		msge =str(message.payload.decode("utf-8"))
		msge = msge.strip()
		print("on_message: " + msge)
		topics = message.topic.split("/")
		if (len(topics)>2):
			print("/"+topics[1]+"/"+topics[2])
			if (topics[2] == "weatherstation"):
				self.storeData(msge)
				return

	def storeData(self, message):
		print("storeData: "+message)
		txt = message.strip()
		values = message.split("|")
		try:
			cursor = self.conn.cursor()
			cursor.execute("INSERT INTO weather (time,location,temperature, pressure,humidity) VALUES (%s,%s,%s,%s,%s);",(datetime.now(),LOCATION,values[1], values[3], values[5]))
		except (Exception, psycopg2.Error) as error:
			print(error.pgerror)
		self.conn.commit()


def main():
	ws = WeatherStation()
	while(1):
		sleep(2)

main()
