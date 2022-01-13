# Weather Station

Code for Raspberry based weather station with space weather twist. Contains two services one for retrieving data from BME280 and one other temperature sensor and one for retrieving Sun corona mass ejection events from NASA DONKI API. Note that you need to create API key for retrieving data from NASA API. 

Weather data is pushed to Timescale database (PostGreSQL) where it can be then retrieved and visualised with Grafana or Superset. Space event are pused to Wordpress Posts. 
