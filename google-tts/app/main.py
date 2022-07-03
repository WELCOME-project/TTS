from io import BytesIO
import socket

import requests
from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

from google.cloud import texttospeech

app = FastAPI()

# Instantiates a client
client = texttospeech.TextToSpeechClient()
@app.get("/")
def hello():
    html = "<h3>TTS</h3>" \
           "<b>Hostname:</b> {hostname}<br/>"

    return html.format(hostname=socket.gethostname())


@app.get(
    "/text2speech",
    responses={
        200: {
            "content": {"audio/mp3": {}},
            "description": "Return the generated audio in mp3 format.",
        }
    }    
    )
def text2speech(text:str = None, language_code:str = "en-US", ssml_gender:str = "NEUTRAL"):
    if text:
        logger.info("Processing text...")

        output = BytesIO()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, ssml_gender=ssml_gender
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        output=response.audio_content

        logger.info("Text processed!")

        return StreamingResponse(BytesIO(output), headers={'Content-Disposition': 'attachment; filename=audio.wav'}, media_type='audio/wav')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
