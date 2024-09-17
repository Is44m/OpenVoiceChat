from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs
from openvoicechat.llm.llm_gpt import Chatbot_gpt
from openvoicechat.stt.stt_hf import Ear_hf
import os
import io

#FOR TESTING ONLY
from typing import Generator


# FastAPI app initialization
app = FastAPI()

load_dotenv()

# Twilio and OpenVoiceChat setup
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
ngrok_tunnel_url = os.getenv('NGROK_TUNNEL_URL')

gpt_api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Initialize OpenVoiceChat components
device = 'cuda'  # Change to 'cpu' if not using GPU
ear = Ear_hf(silence_seconds=2, device=device)

#COMMENTED OUT FOR TESTING. CLOUDFARE ISSUE.
#chatbot = Chatbot_gpt(api_key=gpt_api_key)


mouth = Mouth_elevenlabs(api_key=elevenlabs_api_key)

# Twilio webhook to handle the inbound call
@app.post("/twilio_connect")
async def twilio_connect(request: Request):
    response = VoiceResponse()

    # Generate a TwiML response to stream audio from the call
    connect = Connect()
    agent_id = "default_agent"  # Optional: Use agent-specific logic
    stream_url = f"{ngrok_tunnel_url}/stream_audio/{agent_id}"
    
    connect.stream(url=stream_url)
    response.append(connect)

    return str(response)


#FOR TESTING ONLY:
class MockChatbot:
    def run(self, text_input: str) -> Generator[str, None, None]:
        # Simulated response chunks
        preset_response = "This is a test response from the mock chatbot."
        for i in range(0, len(preset_response), 10):  # Yield chunks of 10 characters
            yield preset_response[i:i+10]

chatbot = MockChatbot()
#---------------------------------------------


# @app.post("/stream_audio/{agent_id}")
# async def stream_audio(agent_id: str, request: Request):
#     # Receive audio data from Twilio
#     voice_data = await request.body()
#     #print("VD: ",voice_data)
#     # Convert audio data to text
#     text_input = ear.transcribe_bytes(voice_data)  # Ensure this method handles raw audio data
    
#     # Get GPT-based response
#     chat_response = chatbot.run(text_input)
#     #print("chat_response: ",chat_response)

#     response_text = ''.join(chunk for chunk in chat_response)
#     # Get the TTS audio data
#     tts_generator = mouth.run_tts_stream(response_text)  # This returns a generator
    
#     # Save the audio data to a file
#     file_path = "C:\\Users\\USER\\Downloads\\outputdirect.wav"
#     with open(file_path, "wb") as f:
#         for chunk in tts_generator:
#             f.write(chunk)
    
#     # To return a streaming response, you still need to convert it to bytes
#     # and send it back as a response if required by the application
#     audio_bytes = io.BytesIO()
#     with open(file_path, "rb") as f:
#         audio_bytes.write(f.read())
    
#     audio_bytes.seek(0)
    
#     # Return the audio data as a StreamingResponse
#     return StreamingResponse(audio_bytes, media_type="audio/wav")


@app.post("/stream_audio/{agent_id}")
async def stream_audio(agent_id: str, request: Request):
    # Receive audio data from Twilio
    voice_data = await request.body()
    print(f"Received voice data of size: {len(voice_data)} bytes")
    
    # Convert audio data to text
    text_input = ear.transcribe_bytes(voice_data)
    print(f"Transcribed text: {text_input}")
    
    # Get GPT-based response
    chat_response = chatbot.run(text_input)
    chat_response_list = list(chat_response)  # Collect chunks into a list
    print(f"Chat response chunks: {chat_response_list}")

    # Check if chunks are being yielded correctly
    if not chat_response_list:
        print("No chunks received from chatbot.")
    response_text = ''.join(chunk for chunk in chat_response_list)

    for chunk in chat_response_list:
        print(f"Chunk: '{chunk}'")

    print(f"Response text: {response_text}")
    
    # Get the TTS audio data
    tts_generator = mouth.run_tts_stream(response_text)
    print("Started TTS generator")
    
    # Save the audio data to a file
    file_path = "C:\\Users\\USER\\Downloads\\outputdirect.wav"
    with open(file_path, "wb") as f:
        for chunk in tts_generator:
            f.write(chunk)
            print(f"Written chunk of size: {len(chunk)} bytes")
    
    # Load the saved file for streaming response
    audio_bytes = io.BytesIO()
    with open(file_path, "rb") as f:
        audio_bytes.write(f.read())
        print(f"Loaded audio file of size: {len(audio_bytes.getvalue())} bytes")
    
    audio_bytes.seek(0)
    
    # Return the audio data as a StreamingResponse
    return StreamingResponse(audio_bytes, media_type="audio/wav")
