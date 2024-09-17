if __name__ == '__main__':
    import torch
    from base import BaseEar
else:
    from .base import BaseEar
import numpy as np


class Ear_hf(BaseEar):
    def __init__(self, model_id='openai/whisper-base.en', device='cpu',
                 silence_seconds=2, generate_kwargs=None, listener=None):
        super().__init__(silence_seconds, listener=listener)
        from transformers import pipeline
        self.pipe = pipeline('automatic-speech-recognition', model=model_id, device=device)
        self.device = device
        self.generate_kwargs = generate_kwargs

    def transcribe(self, audio):
        from torch import no_grad
        with no_grad():
            transcription = self.pipe(audio, generate_kwargs=self.generate_kwargs)
        return transcription['text'].strip()
    def transcribe_bytes(self, audio_bytes):
        from scipy.signal import resample
        from torch import no_grad
        import io
        import soundfile as sf
        
        with no_grad():
            # Convert raw bytes to audio file-like object
            audio_file = io.BytesIO(audio_bytes)
            
            # Read audio data
            try:
                audio_data, sample_rate = sf.read(audio_file)
                print(f"Audio data shape: {audio_data.shape}, Sample rate: {sample_rate}")
                
                # Resample audio if needed
                target_sample_rate = 16000  # Example target sample rate
                if sample_rate != target_sample_rate:
                    num_samples = int(len(audio_data) * float(target_sample_rate) / sample_rate)
                    audio_data = resample(audio_data, num_samples)
                    sample_rate = target_sample_rate
                    print(f"Resampled audio data shape: {audio_data.shape}, Sample rate: {sample_rate}")
                
            except Exception as e:
                print(f"Error reading audio data: {e}")
                return ""
            
            # Perform transcription
            try:
                transcription = self.pipe(audio_data, **(self.generate_kwargs or {}))
                print(f"Transcription output: {transcription}")
            except Exception as e:
                print(f"Error during transcription: {e}")
                return ""
        
        # Handle transcription output
        transcribed_text = transcription.get('text', '').strip()
        return transcribed_text
    def transcribe_bytes(self, audio_bytes):
        from torch import no_grad
        import io
        import soundfile as sf
        from scipy.signal import resample
        
        with no_grad():
            # Convert raw bytes to audio file-like object
            audio_file = io.BytesIO(audio_bytes)
            
            # Read audio data
            try:
                audio_data, sample_rate = sf.read(audio_file)
                
                # Resample audio if needed
                target_sample_rate = 16000  # Example target sample rate
                if sample_rate != target_sample_rate:
                    num_samples = int(len(audio_data) * float(target_sample_rate) / sample_rate)
                    audio_data = resample(audio_data, num_samples)
                    sample_rate = target_sample_rate
                
            except Exception as e:
                # Handle errors appropriately
                return ""
            
            # Perform transcription
            try:
                transcription = self.pipe(audio_data, **(self.generate_kwargs or {}))
            except Exception as e:
                # Handle errors appropriately
                return ""
        
        # Handle transcription output
        transcribed_text = transcription.get('text', '').strip()
        return transcribed_text




if __name__ == "__main__":
    import torchaudio
    import torchaudio.functional as F

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    ear = Ear_hf(device=device)

    audio, sr = torchaudio.load('../media/abs.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.transcribe(np.array(audio))
    print(text)

    text = ear.listen()
    print(text)
