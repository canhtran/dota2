### Warning
Currently, the opendota api had problem with their server, using a simple search query with common username like ```https://api.opendota.com/api/search?q=Hi``` will took very long time to recieve results. It causes infinite loop, please avoid to test with common username. Thanks  (The issue has been indentified and the solution is at the bugs section)

### Objective
The objective is to write a Facebook Messenger bot in Python, which read username (account_id) of player and return some statistics.

### Tech Stack
The tech stack that was used is:
- ```AWS EC2``` for backend hosting. The free tier is more than enough for demo purpose.
- ```Python``` is language of choice. The version that was used is 3.6
- ```Flask``` as the web development framework. It’s a very lightweight framework that’s perfect for small scale projects/microservices.
- ```XGBoost``` for building model.
- ```Gunicorn``` and ```Nginx``` for serve our python code (Flask is not safe for production) and web server in EC2
- Worth to mention ```Let's Encrypt``` for config SSL on AWS EC2 with my custom domain

### Messenger bot
I've never used this API. My experience with chat bot platform mostly in Slack and Telegram. I spent around 3 hours to check the doc and build simple echo bot.

Facebook bot is quite easy to use. The bots are constituted by a server that responds to two types of requests:

- GET requests are being used for authentication. They are sent by Messenger with an authentication code that you register on FB.
- POST requests are being used for the actual communication. The typical workflow is that the bot will initiate the communication by sending the POST request with the data of the message sent by the user, we will handle it, send a POST request of our own back. If that one is completed successfully (a 200 OK status is returned) we also respond with a 200 OK code to the initial Messenger request.

### Dota API
Based on the requirement, the ```dota2api``` is not supported with username searching. So I switch to another opensource dota api call ```opendota```. It's good that ```opendota``` is built as a REST api so I have to write the interface by using ```requests``` python package.

### Bot server
At first I design the architect like this:

![alt text](https://github.com/canhtran/dota2/blob/master/bot/img/server-architect.jpg?raw=true)

There are two servers: webhook server and recommendation engine.
- Webhook is built for receive, processing messages, do simple statistics
- Recommendation engine is used for automatically crawling the new data by ```crawler_bot```, train new model and store all data in MySQL.

With the limited of time, I get rid of MySQL and recommedation engine server. The crawler bot ```crawler_bot.py``` will run and store all data in csv file format then I train the model using ```train_xgboost.py```. Finally I put the pickle file to webhook server and call directly there. This architect above may use for future scalable.

With the Webhook / Webserver/ HTTP Requests, I have some of choices in here:
- Django
- Flask
- AWS Lambda.

For AWS Lambda, It doesn't support the external library like numpy/xgboost/pickle. If I want to deploy, I have to copy the source code of the library and upload together with my code. It's not a good idea in here especially if I want to scale the system in the future.

I'm familiar with Django Rest API Framework. I've used Django alot but then come with the infrastructure, that's quite heavy and time consuming.

I decided to stick with Flask for development and simple EC2 configuration. On EC2, I use Gunicorn as a wsgi server to run my code since Flask is not safe for production and Nginx for webserver.

### Recommendation
For recommendation, as a dota 2 player I'm not very keen on recommend heroes based on user profile. There are 113 heroes and mostly players pick the heroes based on their interest and usually play random (like me =]] ). Moreover, most of the studies about dota2, they build the recommendation based on the match where we know the enemy team's heroes and heroes in our team to point out which hero the player should pick.

But as the requirement, with only User Profile, I will "hack" the recommendation engine.
- Firstly, I created the heroes mapping files ```recommenation/data/heroes.csv``` base on my knowledge about dota2. This file contains heroes information and main role of heroes in current meta game (version 7.06c). There are for main roles/positions: ```mid, carry, support and offlane.```
- Secondly, I made a ```crawler_bot``` to get the information of Pro Players (total 1000 players).
- Thirdly, With the data, I extract the features from profiles: ```kills, deaths, assists, last_hit, denies, xp_per_min, gold_per_min, kda```. All are the mean value.
- Each player will have a position in a team, I get the top hero that he/she played, look up in the heroes mapping file and extract the main position of that player.
- Due to the time constraint, I built a simple model using XGBClassifier with main_roles as the label and the features above.
- Finally, with the position as result, I do a random look up in the heroes files to recommend heroes for player with the play styles from dotafire.

The hypothesis in here is, if a player is suggested to play in a fixed position, e.g support. He/she will tend to do random picking the heroes which belong to support roles.

In conclusion, dota 2 is a game mostly based on heuristic of player to pick the hero, so the result is only acceptable and limit for show case.

### Go further
This chat is basic, it doesn't let user to "ask a question". That would probably I would follow for continuing the project. Maybe a NLP system to detect simple question with "what" and "who".

Secondly, I would enhance the architect, separate the Recommendation engine and  plug-in database MySQL since MySQL is the most common RDMS. It works quite good with Flask SQLAlchemy. Also the asynchronous haven't considered in here. Right now, it keeps the connection between Messenger and API for the whole process (which take several seconds in the worst case). This may causing the loop, because if the messenger doesn't received 200 OK response after a period of time, it will continue POST the requests to our API.

Finally, definitely about the recommendation, I don't have time to tuning the model so the accuracy is quite bad 59%. Features are not normalized yet. In the future, I would use the matches database to predict the next hero that player should pick or ask a few questions to recommend heroes to players.

### Bugs
Some of the bugs may be happened due to the asynchronize of the architect.

E.g If user key in a common username like "Test" or "Invoker". It tooks around 5s to query from opendota api and send back to webhook. Counting the time latency between Messenger and Webhook, total it tooks around 10s. Because the waiting time is long, facebook will send another POST request to webhook cause the duplicate in the bot answer. It may causing the infinitive loops. 

To avoid this happen, I have to change the architect, separate webhook server into 2 smaller server. One calls ```webhook_handle_service``` for webhook to handle the message, immediately reply 200Ok back to messenger bot. And another server api ```message_handle_api``` to receive message from webhook_handle_api and process with the message.
