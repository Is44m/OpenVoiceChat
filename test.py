import os
from fastapi import FastAPI, Request, HTTPException
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs
from openvoicechat.llm.llm_gpt import Chatbot_gpt
from openvoicechat.stt.stt_hf import Ear_hf
from openvoicechat.utils import run_chat

app = FastAPI()

# Load environment variables
load_dotenv()
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
gpt_api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

# Twilio client initialization
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# OpenVoiceChat components
device = 'cuda'
ear = Ear_hf(silence_seconds=2, device=device)
chatbot = Chatbot_gpt(api_key=gpt_api_key)
mouth = Mouth_elevenlabs(api_key=elevenlabs_api_key)

# Endpoint for making a call
@app.post("/call")
async def make_call(request: Request):
    data = await request.json()
    recipient_number = data.get("recipient_phone_number")
    agent_id = data.get("agent_id", "default_agent")

    if not recipient_number:
        raise HTTPException(status_code=400, detail="Recipient phone number required.")

    # Make a call using Twilio
    call = twilio_client.calls.create(
        to=recipient_number,
        from_=twilio_phone_number,
        url=f"{request.url_for('twilio_connect')}?agent_id={agent_id}",
        method="POST"
    )

    return {"status": "Call initiated", "call_sid": call.sid}

# Twilio webhook for handling the call and voice interaction
@app.post("/twilio_connect")
async def twilio_connect(agent_id: str):
    response = VoiceResponse()

    connect = Connect()
    stream_url = f"{os.getenv('NGROK_TUNNEL_URL')}/stream_audio/{agent_id}"
    connect.stream(url=stream_url)
    response.append(connect)

    return str(response)

# Handle the audio stream from Twilio
@app.post("/stream_audio/{agent_id}")
async def stream_audio(agent_id: str, request: Request):
    voice_data = await request.body()
    
    # Process voice data through OpenVoiceChat
    text_input = ear.recognize(voice_data)
    chat_response = chatbot.get_response(text_input)
    tts_output = mouth.speak(chat_response)

    # Send synthesized voice response back to Twilio (streamed)
    return tts_output
