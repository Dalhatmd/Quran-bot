#!/usr/bin/env python3
""" whatsapp Qur'an bot """
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests
import schedule
import time
import threading

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
API_ENDPOINT = 'https://api.alquran.cloud/v1/ayah/{ayah_number}/en.asad'
subscribed_users = set()    #TODO: Use aa database in prod

def fetch_random_ayah():
    """ gets a random ayah"""
    import random
    ayah_number = random.randint(1, 6236)   #get a random verse
    url = API_ENDPOINT.format(ayah_number=ayah_number)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        ayah = data['data']['text']
        surah = ['data']['surah']['englishName']
        return f"📖 *{surah}* - Ayah {number}:\n{ayah}"
    else:
        return "Unable to fetch Ayah at this time"

def send_daily_ayah():
    """functionality to send ayah"""

