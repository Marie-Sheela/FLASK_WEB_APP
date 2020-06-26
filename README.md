How to use?

1.	Clone the git repository
2.	Enter values into key.json – The value from Google Vision module.
3.	Fill up below values in app.py. The values are generated while creating account to Fitbit.
a.	CLIENT_ID = ‘xxxxx'
b.	CLIENT_SECRET = ‘xxxxxx’
4.	Install below Python Modules:
a.	pip install Flask 
b.	pip install opencv-python
c.	pip install fitbit
d.	pip install cherrypy
e.	pip install pandas
f.	pip install google-cloud 
g.	pip install google-cloud-vision
h.	pip install pyserial
5.	Copy the Arduino sketch.py to your Mega2560 board.
6.	Run the Flask application on the browser. Click on the start button once the “Username” and “Questionnaire” results are selected.
7.	The Video popup window starts. It uses OpenCV to process the video and Google vision analyses it in Realtime. Close it after 10-20 seconds.
8.	Fitbit authentication window opens up in another tab. It fetches the data from Fitbit.
9.	The algorithm processes the inputs based on valence- arousal graph.
10.	A popup opens to show the user emotion. Click ok.
11.	The LED corresponding to IoT lights up.
