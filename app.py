from flask import Flask, request
import json
import requests
from flask_sqlalchemy import SQLAlchemy
import os
import praw

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
reddit = praw.Reddit(client_id='oSX_k9ERfsDcjA',
                     client_secret='uGdRuM0V2O4gL-Gw7LNA7KL_nAw',
                     user_agent='my user agent')

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAACAGvJVipcBAFvsThqtUTZBoKtl0tAKUgiopMern9Wudajq7NZATBoCiOUSucQHPZAjrXFpbMRZBZAsyU4XQLlrHGLH33jd3HCKX6JY295PQEdJuf8XIktQ3fZC11ZBFDrhgremG8uzHgXn1udArzHFBj46vlNHXj7VgZChrc0fuwZDZD'

quick_replies_list = [{
    "content_type":"text",
    "title":"Meme",
    "payload":"meme",
},
{
    "content_type":"text",
    "title":"Motivation",
    "payload":"motivation",
},
{
    "content_type":"text",
    "title":"Shower Thought",
    "payload":"Shower_Thought",
},
{
    "content_type":"text",
    "title":"Jokes",
    "payload":"Jokes",
}
]

leagues_quick_replies_list = [{
    "content_type":"text",
    "title":"Premier League",
    "payload":"english",
},
{
    "content_type":"text",
    "title":"League 1",
    "payload":"french",
},
{
    "content_type":"text",
    "title":"Bundesliga",
    "payload":"german",
},
{
    "content_type":"text",
    "title":"Seria A",
    "payload":"italian",
}
]

@app.route('/', methods=['GET'])
def handle_verification():
# when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

# @app.route('/', methods=['POST'])
# def handle_messages():
#     print("Handling Messages")
#     payload = request.get_data()
#     print(payload)
#     for sender, message in messaging_events(payload):
#         print("Incoming from %s: %s" % (sender, message))
#         send_message(PAT, sender, message)
#     return "ok"

# def messaging_events(payload):
#     """Generate tuples of (sender_id, message_text) from the
#     provided payload.
#     """
#     data = json.loads(payload)
#     messaging_events = data["entry"][0]["messaging"]
#     for event in messaging_events:
#         if "message" in event and "text" in event["message"]:
#             yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
#         else:
#             yield event["sender"]["id"], "I can't echo this"

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    print(data)

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message").get("attachments"):
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    lat = messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["lat"]
                    longi = messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["long"]

                    send_location(PAT, sender_id, lat, longi)

                else:  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(PAT, sender_id, message_text)

    return "ok", 200


def send_location(token, recipient, lat, longi):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?' + "lat=" + str(lat) + "&lon=" + str(longi) + '&APPID=facf3a7876343295f70bb6b943e3452c')
    json_obj = r.json()
    temp_k = float(json_obj['main']['temp'])
    temp_c = str(round((temp_k - 273.15), 2))

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": temp_c + " °C",
                            "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})


@app.route('/', methods=['GET'])
def getLeagueTable(leagueId):
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': 'e6bbc2613aca45cba78976ceb341858d', 'X-Response-Control': 'minified' }
    connection.request('GET', '/v1/competitions/' + str(leagueId) + '/leagueTable', None, headers )
    response = json.loads(connection.getresponse().read().decode())

    #Prints league table
    s = ""
    for team in response['standing']:
        s+=str(team['rank']) + ". " + str(team['team']) + "\n"

    return s


# @app.route('/', methods=['GET'])
# def send_weather():
#     r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Ottawa,Canada&APPID=facf3a7876343295f70bb6b943e3452c')
#     json_obj = r.json()
#     temp_k = float(json_obj['main']['temp'])
#     temp_c = str(round((temp_k - 273.15), 2))

#     return temp_c


def send_message(token, recipient, text):

    """Printing values of tables for testing"""
    # print("USERS:")
    # for u in db.session.query(Users).all():
    #     print(u.__dict__)
    # print("POSTS:")
    # for u in db.session.query(Posts).all():
    #     print(u.__dict__)
    print("USER INPUT ISSSSS: " + text.lower())
    """Send the message text to recipient with id recipient.
    """
    if "meme" in text.lower():
        user_input = "memes"
    elif "shower" in text.lower():
        user_input = "Showerthoughts"
    elif "joke" in text.lower():
        user_input = "Jokes"
    elif "motivation" in text.lower():
        user_input = "GetMotivated"
    elif "weather" in text.lower():
        # temp = send_weather()
        user_input = "weather"
    elif "standings" in text.lower():
        user_input = "standings"
    elif "english" in text.lower():
        user_input = "445"
    else:
        user_input = ""


    myUser = get_or_create(db.session, Users, name=recipient)

    if user_input == "Showerthoughts":
        for submission in reddit.subreddit(user_input).hot(limit=None):
            if (submission.is_self == True):
                query_result = Posts.query.filter(Posts.name == submission.id).first()
                if query_result is None:
                    myPost = Posts(submission.id, submission.title)
                    myUser.posts.append(myPost)
                    db.session.commit()
                    payload = submission.title
                    break
                elif myUser not in query_result.users:
                    myUser.posts.append(query_result)
                    db.session.commit()
                    payload = submission.title
                    break
                else:
                    continue  

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": payload,
                            "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})
    
    elif user_input == "Jokes":
        for submission in reddit.subreddit(user_input).hot(limit=None):
            if ((submission.is_self == True) and ( submission.link_flair_text is None)):
                query_result = Posts.query.filter(Posts.name == submission.id).first()
                if query_result is None:
                    myPost = Posts(submission.id, submission.title)
                    myUser.posts.append(myPost)
                    db.session.commit()
                    payload = submission.title
                    payload_text = submission.selftext
                    break
                elif myUser not in query_result.users:
                    myUser.posts.append(query_result)
                    db.session.commit()
                    payload = submission.title
                    payload_text = submission.selftext
                    break
                else:
                    continue  

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": payload}
            }),
            headers={'Content-type': 'application/json'})

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": payload_text,
                            "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})
        
    elif user_input == "GetMotivated" or user_input == "memes":
        payload = "http://imgur.com/WeyNGtQ.jpg"
        for submission in reddit.subreddit(user_input).hot(limit=None):
            if (submission.link_flair_css_class == 'image') or ((submission.is_self != True) and ((".jpg" in submission.url) or (".png" in submission.url))):
                query_result = Posts.query.filter(Posts.name == submission.id).first()
                if query_result is None:
                    myPost = Posts(submission.id, submission.url)
                    myUser.posts.append(myPost)
                    db.session.commit()
                    payload = submission.url
                    break
                elif myUser not in query_result.users:
                    myUser.posts.append(query_result)
                    db.session.commit()
                    payload = submission.url
                    break
                else:
                    continue

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"attachment": {
                              "type": "image",
                              "payload": {
                                "url": payload
                              }},
                              "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})

    elif user_input == "weather":
        # r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        #     params={"access_token": token},
        #     data=json.dumps({
        #         "recipient": {"id": recipient},
        #         "message": {"text": temp + " °C",
        #                     "quick_replies":quick_replies_list}
        #     }),
        #     headers={'Content-type': 'application/json'})


        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": "Please share your location:",
                            "quick_replies":[{"content_type":"location"}]}
            }),
            headers={'Content-type': 'application/json'})

    elif user_input == "standings":
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": "Please pick a league:",
                            "quick_replies":leagues_quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})

    #english league
    elif user_input == "445":
        standings = getLeagueTable(user_input)

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": standings,
                            "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})

    
    else:
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": "Sorry, I didn't get that.",
                            "quick_replies":quick_replies_list}
            }),
            headers={'Content-type': 'application/json'})
    

    if r.status_code != requests.codes.ok:
        print(r.text)

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

relationship_table=db.Table('relationship_table',                            
    db.Column('user_id', db.Integer,db.ForeignKey('users.id'), nullable=False),
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'),nullable=False),
    db.PrimaryKeyConstraint('user_id', 'post_id') )
 
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    posts=db.relationship('Posts', secondary=relationship_table, backref='users' )  

    def __init__(self, name=None):
        self.name = name
 
class Posts(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    url=db.Column(db.String, nullable=False)

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url

if __name__ == '__main__':
    app.run()