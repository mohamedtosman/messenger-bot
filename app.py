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

# quick_replies_list = [{
#     "content_type":"text",
#     "title":"Meme",
#     "payload":"meme",
# },
# {
#     "content_type":"text",
#     "title":"Motivation",
#     "payload":"motivation",
# },
# {
#     "content_type":"text",
#     "title":"Shower Thought",
#     "payload":"Shower_Thought",
# },
# {
#     "content_type":"text",
#     "title":"Jokes",
#     "payload":"Jokes",
# }
# ]

quick_replies_list = [{
    "content_type":"text",
    "title":"All",
    "payload":"all",
},
{
    "content_type":"text",
    "title":"Memes",
    "payload":"memes",
},
{
    "content_type":"text",
    "title":"News",
    "payload":"news",
},
{
    "content_type":"text",
    "title":"Soccer",
    "payload":"soccer",
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
def send_weather():
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Ottawa,Canada&APPID=facf3a7876343295f70bb6b943e3452c')
    json_obj = r.json()
    temp_k = float(json_obj['main']['temp'])
    temp_c = str(round((temp_k - 273.15), 2))

    return temp_c


def send_message(token, recipient, text):

    """Printing values of tables for testing"""
    # print("USERS:")
    # for u in db.session.query(Users).all():
    #     print(u.__dict__)
    # print("POSTS:")
    # for u in db.session.query(Posts).all():
    #     print(u.__dict__)

    """Send the message text to recipient with id recipient.
    """
    # if "meme" in text.lower():
    #     subreddit_name = "memes"
    # elif "shower" in text.lower():
    #     subreddit_name = "Showerthoughts"
    # elif "joke" in text.lower():
    #     subreddit_name = "Jokes"
    # elif "motivation" in text.lower():
    #     subreddit_name = "GetMotivated"
    # elif "weather" in text.lower():
    #     # temp = send_weather()
    #     subreddit_name = "weather"
    # else:
    #     subreddit_name = ""


    if "all" in text.lower():
        subreddit_name = "all"
    elif "memes" in text.lower():
        subreddit_name = "memes"
    elif "news" in text.lower():
        subreddit_name = "news"
    elif "soccer" in text.lower():
        subreddit_name = "soccer"
    elif "weather" in text.lower():
        # temp = send_weather()
        subreddit_name = "weather"
    else:
        subreddit_name = ""

    myUser = get_or_create(db.session, Users, name=recipient)

    if subreddit_name == "news":
        for submission in reddit.subreddit(subreddit_name).hot(limit=None):
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
    
    elif subreddit_name == "soccer":
        for submission in reddit.subreddit(subreddit_name).hot(limit=None):
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
        
    elif subreddit_name == "all" or subreddit_name == "memes":
        payload = "http://imgur.com/WeyNGtQ.jpg"
        for submission in reddit.subreddit(subreddit_name).hot(limit=None):
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

    elif subreddit_name == "weather":
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