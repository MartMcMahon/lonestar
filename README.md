Lonestar is an http endpoint for my Amazon Echo written in python that runs on a raspberry pi in my home.
The Alexa Skill calls a Lambda function that passes along input from the echo, to the pi, then gets the output from the http request and sends that back out to be spoken.

One of the background process on the pi, is getting an updated schedule of bus times for the 3 routes I always take to work.
The server keeps all bus data in a database so that it is available as soon as the request is made.
The skill is started by speaking "Alexa, ask lonestar when the next bus comes" and the result is the next arrival of the relevant busses at the stops I hardcoded in.

Another thing the web server can do is run shell commands.
There is an endpoint for running omxplayer which is the video player I've been using.
I'm currently working on the database of movies and shows I have downloaded so it can use that when I give it parameters.
