# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
stream_url = os.environ["STREAM_URL"]
client = Client(account_sid, auth_token)

twiml = f"""<Response><Connect><Stream name="Example Audio Stream" url="{stream_url}" /></Connect><Say>The stream has 
started.</Say></Response>"""

call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to="+923202571157",
    from_="+15418723888"
)

print(call.sid)
print(client)
