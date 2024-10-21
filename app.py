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
    ayah_number = random.randint(1, 6236)
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
    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message_body = fetch_random_ayah()

    for user in subscribed_users:
        try:
            message = client.messages.create(
                      body=message.body,
                      from_=f'whatsapp: {TWILIO_WHATSAPP_NUMBER',
                      to=f'whatsapp: {user}'
                      )
            print(f'Message Sent to {user}. message SID: {message.sid}')
        except Exception as e:
            print('Failed to send message')

def run_scheduler():
    """ Handles the time daily ayah is sent"""
    time = '9:00'
    schedule.every().day.at(time).do(send_daily_ayah)
    while True:
        schedule.run_pending()
        time.sleep(60)


@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '').replace('whatsapp:', '')
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == 'subscribe':
        if from_number in subscribed_users:
            msg.body("You are already subscribed to daily Qur'an verses.")
        else:
            subscribed_users.add(from_number)
            msg.body("✅ You have subscribed to receive a daily Qur'an verse every day at 9 AM.")
    elif incoming_msg == 'unsubscribe':
        if from_number in subscribed_users:
            subscribed_users.remove(from_number)
            msg.body("❌ You have unsubscribed from daily Qur'an verses.")
        else:
            msg.body("You are not subscribed.")
    else:
        msg.body("Welcome to the Qur'an Bot! Send 'subscribe' to receive a daily Qur'an verse or 'unsubscribe' to stop.")

    return str(resp)

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

