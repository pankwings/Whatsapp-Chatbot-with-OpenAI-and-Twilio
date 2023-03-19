import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
import os
import sys

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
whatsapp_phone_number = os.getenv("WHATSAPP_PHONE_NUMBER")

app = Flask(__name__)

# Create a Twilio client object with your account SID and auth token
client = Client(account_sid, auth_token)

# Default message on the home page.
@app.route('/')
def home():
    return 'All the best brother !'

# Create a list to store the last 10 conversations/queries
history = []

# Handle incoming messages
@app.route('/incoming', methods=['POST'])
def handle_incoming_message():
    try:
        incoming_message = request.form['Body']
        
        if incoming_message.lower() == 'restart':
            print('Restarting app...')
            # You can replace the command with the appropriate command to restart your app
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            # Add the new message to the history list
            history.append(f"user query: {incoming_message}")

            # Remove the oldest message if the history list size is greater than 10
            if len(history) > 10:
                history.pop(0)
            
            # Pass the history list to ChatGPT with message indicating it's previous user messages
            prompt = incoming_message+"\nThese messages below are my previous messages:\n" + "\n".join(history) + "\nPlease use these as a backup when the current message is not sufficient or more information is needed.\n"
            print(prompt)
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=prompt,
                max_tokens=600,
                n=1,
                stop=None,
                temperature=0.7
            )["choices"][0]["text"].strip()

            # Add the ChatGPT response to the history list
            history.append(f"text-davinci-002 response: {response}")
            print("HISTORY:\n",history)
            # Remove the oldest message if the history list size is greater than 10
            if len(history) > 10:
                history.pop(0)
            
            # Create a Twilio MessagingResponse object
            twilio_response = MessagingResponse()

            # Add the response to the Twilio MessagingResponse object
            twilio_response.message(response)

            # Send the response back to the user
            message = client.messages.create(
                body=response,
                from_=twilio_phone_number,
                to=whatsapp_phone_number
            )

            # Print the message SID
            print("Message SID:", message.sid)

            # Return the Twilio MessagingResponse object
            # return str(twilio_response)
    except:
        pass
    return 'OK',200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)