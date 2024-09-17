import os
from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs
from openvoicechat.tts.tts_xtts import Mouth_xtts
from openvoicechat.llm.llm_gpt import Chatbot_gpt
from openvoicechat.llm.llm_llama import Chatbot_llama
from openvoicechat.stt.stt_deepgram import Ear_deepgram
from openvoicechat.stt.stt_hf import Ear_hf
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv
load_dotenv()


if __name__ == "__main__":
    device = 'cpu'

    print('loading models... ', device)
    #api_key = os.getenv('DEEPGRAM_API_KEY')
    # ear = Ear_deepgram(silence_seconds=2, api_key=api_key)
    ear = Ear_hf(silence_seconds=2, device=device)

    load_dotenv()

    chatbot = Chatbot_gpt(sys_prompt=llama_sales)

    mouth = Mouth_xtts(device=device)

    run_chat(mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: '[END]' in x)
