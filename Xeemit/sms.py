from twilio.rest import TwilioRestClient
from pprint import pprint  # debug

from phonenumbers import carrier  # pip install phonenumbers
import phonenumbers

from config import Twilio_accnt_sid, Twilio_auth_tok, Twilio_number


account_sid = Twilio_accnt_sid
auth_token  = Twilio_auth_tok  

client = TwilioRestClient(account_sid, auth_token)


def textmsg(phonenumber, msg, countrycode):
    number = phonenumbers.parse(phonenumber, countrycode)
    if carrier.name_for_number(number, 'en') != '':
        message = client.messages.create(body=msg, to=phonenumber, from_="+13177933648")
        pprint(message.sid)
        return True
    else: return False


def verification_textmsg(number, code):
    message = client.messages.create(body="Your Xeemit verification code is: "+code,
            to=number,    # Replace with your phone number
            from_=Twilio_number)  # Replace with your Twilio number
    pprint(message.sid)