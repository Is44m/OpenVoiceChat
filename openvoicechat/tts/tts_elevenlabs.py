if __name__ == '__main__':
    from base import BaseMouth
else:
    from .base import BaseMouth
from dotenv import load_dotenv
from pydub import AudioSegment
import io
import numpy as np
import sounddevice as sd
import requests
import os


class Mouth_elevenlabs(BaseMouth):
    def __init__(self, model_id='eleven_turbo_v2',
                 voice_id='IKne3meq5aSn9XLyUdCD',
                 api_key='',
                 player=sd):
        self.model_id = model_id
        self.voice_id = voice_id
        if api_key == '':
            load_dotenv()
            api_key = os.getenv('ELEVENLABS_API_KEY')
        self.api_key = api_key
        super().__init__(sample_rate=44100, player=player)

    def run_tts(self, text):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": f"{self.api_key}"
        }

        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)
        audio_segment = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")

        samples = np.array(audio_segment.get_array_of_samples())

        return samples

    
    # def run_tts_stream(self, text):
    #     url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
    #     headers = {
    #         "Accept": "audio/mpeg",
    #         "Content-Type": "application/json",
    #         "xi-api-key": f"{self.api_key}"
    #     }

    #     data = {
    #         "text": text,
    #         "model_id": self.model_id,
    #         "voice_settings": {
    #             "stability": 0.5,
    #             "similarity_boost": 0.5
    #         }
    #     }

    #     # Send the request with streaming enabled
    #     with requests.post(url, json=data, headers=headers, stream=True) as response:
    #         response.raise_for_status()  # Ensure we raise an exception for HTTP errors

    #         # Yield audio chunks as they are received
    #         for chunk in response.iter_content(chunk_size=4096):
    #             if chunk:
    #                 audio_segment = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
    #                 samples = np.array(audio_segment.get_array_of_samples())
    #                 yield samples
    # def run_tts_stream(self, text):
    #     url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
    #     headers = {
    #         "Accept": "audio/mpeg",
    #         "Content-Type": "application/json",
    #         "xi-api-key": f"{self.api_key}"
    #     }

    #     data = {
    #         "text": text,
    #         "model_id": self.model_id,
    #         "voice_settings": {
    #             "stability": 0.5,
    #             "similarity_boost": 0.5
    #         }
    #     }

    #     # Create a BytesIO object to accumulate the audio data
    #     audio_stream = io.BytesIO()

    #     # Send the request with streaming enabled
    #     with requests.post(url, json=data, headers=headers, stream=True) as response:
    #         response.raise_for_status()  # Ensure we raise an exception for HTTP errors

    #         # Write audio chunks to the BytesIO object
    #         for chunk in response.iter_content(chunk_size=4096):
    #             if chunk:
    #                 audio_stream.write(chunk)

    #     # Reset the stream position to the beginning
    #     audio_stream.seek(0)

    #     # Process the accumulated audio data
    #     audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
    #     samples = np.array(audio_segment.get_array_of_samples())
        
    #     # Close the BytesIO object
    #     audio_stream.close()

    #     # Yield the samples
    #     yield samples
    def run_tts_stream(self, text):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency=4"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": f"{self.api_key}"
        }

        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        # Create a BytesIO object to accumulate the audio data
        audio_stream = io.BytesIO()

        # Send the request with streaming enabled
        with requests.post(url, json=data, headers=headers, stream=True) as response:
            response.raise_for_status()  # Ensure we raise an exception for HTTP errors

            # Write audio chunks to the BytesIO object
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    audio_stream.write(chunk)

        # Reset the stream position to the beginning
        audio_stream.seek(0)

        # Convert MP3 to WAV
        audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        # Yield WAV data
        yield wav_io.read()


if __name__ == '__main__':

    mouth = Mouth_elevenlabs()

    text = ("If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
            "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
            "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
            "of human-driven cars.")
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
