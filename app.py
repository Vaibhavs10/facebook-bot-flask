import os
import sys
import json
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    #send_message(sender_id, "We're still testing!")
                    send_generic_message(sender_id)
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    payload = messaging_event["postback"]["payload"]  # the message's text
                    if payload == 'C':
                        send_message(sender_id, "Working")
                    else:
                        send_message(sender_id, "We're glad you're helping us test")
                    #send_message(sender_id, payload)

    return "ok", 200

def send_generic_message(recipient_id):
    log("sending generic message to {recipient}: {text}".format(recipient=recipient_id, text="Generic Template"))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
    headers = {
        "Content-Type": "application/json"
        }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements":[
                        {
                            "title": "Hello!",
                            "item_url": "http://vaibhavs10.in",
                            "image_url": "http://loremflickr.com/100/100",
                            "subtitle": "The solution to all your needs!",
                            "buttons":[
                                {
                                    "type": "web_url",
                                    "url": "http://vaibhavs10.in",
                                    "title": "View Website"
                                },
                                {
                                    "type": "postback",
                                    "title": "Start Chatting",
                                    "payload": "C"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_image_url(recipient_id, image_url):
    log("sending image file url to {recipient}: {text}".format(recipient=recipient_id, text=image_url))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
    headers = {
        "Content-Type": "application/json"
        }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_action(recipient_id, action):
    #Action can be "mark_seen", "typing_on", "typing_off"
    log("sending action to {recipient}: {text}".format(recipient=recipient_id, text=action))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
    headers = {
        "Content-Type": "application/json"
        }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
            },
        "message": {
            "attachment": {
                "type": "file",
                "payload": {
                    "url": file_url
                    }
                }
            }
        })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_file_url(recipient_id, file_url):
    log("sending file url to {recipient}: {text}".format(recipient=recipient_id, text=file_url))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
    headers = {
        "Content-Type": "application/json"
        }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "file",
                "payload": {
                    "url": file_url
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def quick_reply(recipient_id, message_text, text):
    log("sending quick message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies":[
                {
                    "content_type": "text",
                    "title": text,
                    "payload": text
                }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message_button_web_url(recipient_id, message_text, web_url, title):

    log("sending button w/ web url to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message_text,
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": web_url,
                            "title": title
                        }
                    ]
                    }
                }
            }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
