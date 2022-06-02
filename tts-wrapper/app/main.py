from io import BytesIO
import json
import traceback
import requests
import soundfile as sf
import numpy as np
import hashlib
import os

from pathlib import Path
from starlette.responses import StreamingResponse
from starlette.responses import Response
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

CACHE_DIR = None
if ("CACHE_DIR" in os.environ):
    CACHE_DIR = os.environ["CACHE_DIR"]

def manage_exception(module_name, exc):
    logger.exception(module_name + " error")

    detail = {
        "customData": {
            "module": module_name,
            "type": type(exc).__name__,
            "message": str(exc)
        }
    }
    raise HTTPException(status_code=500, detail=detail)

@app.on_event("startup")
async def load_language_config():
    with open("language_config.json") as fd:
        app.state.data = json.load(fd)

@app.get("/")
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/available_languages")
async def available_languages(request: Request):
    language_config = request.app.state.data
    
    data = {}
    data["text2speech"] = list(language_config["text2speech"].keys())
    
    return data

@app.post("/text2speech")
async def synthesize_text_post(request: Request, text: str = Form(...), language: str = Form("en")):
    text2speech = request.app.state.data["text2speech"].get(language)
    return synthesize_text(text2speech["url"], text, language, text2speech["params"])

@app.get("/text2speech")
async def synthesize_text_get(request: Request, text: str, language: str = "en"):
    text2speech = request.app.state.data["text2speech"].get(language)
    return synthesize_text(text2speech["url"], text, language, text2speech["params"])

def preprocess(chunk,language):
    if (language == 'el_male'):
        if (chunk != chunk.rstrip('.')):
            chunk = chunk.rstrip('.')
            print("normalized chunk:")
            print(chunk)
    return chunk


def synthesize_text(text2speech_url, text: str, language: str = "en", params = None):

    print("=======\nstarting to synthesize:")
    print(text)
    try:
        print("language:", language, "\turl:",text2speech_url)
        if text2speech_url is None:
            raise Exception(f"Text2Speech: Language '{language}' not supported!")

        audios = []
        samplerate = None # gets set inside the loop
        headers = None # gets set inside the loop

        chunks = text.split('\n\n')
        for chunk in chunks:
            print("chunk:")
            print(chunk)
            chunk = preprocess(chunk,language)
            md5 = hashlib.md5((language+":"+chunk).encode('utf-8')).hexdigest()
            audio_bytes = None
            if CACHE_DIR is not None and os.path.isfile(os.path.join(CACHE_DIR,md5)):
                audio_bytes = BytesIO(Path(os.path.join(CACHE_DIR,md5)).read_bytes())
            else:
                params["text"] = chunk
                result = sendRequest(text2speech_url, params)
                if headers is None:
                    headers= result.headers
                    print(headers)
                audio_bytes = BytesIO(result.content)
                if CACHE_DIR is not None:
                    Path(os.path.join(CACHE_DIR,md5)).write_bytes(audio_bytes.getvalue())

            print("received ", audio_bytes.getbuffer().nbytes, " bytes")
            audio, samplerate = sf.read(audio_bytes)
            audios.append(audio)
            print("appended chunk audio to list")

        combined = np.concatenate(audios)

        out = BytesIO()
        sf.write(out, combined, samplerate=samplerate, format="wav")

        print("samplerate:",samplerate)
        print("returning concatenated audio (", out.getbuffer().nbytes, " bytes)")

        if headers is None:
            headers = {'Content-Type':'audio/wav'}
        return Response(content=out.getvalue(), media_type=headers['Content-Type'])

    except Exception as exc:
        manage_exception("Synthesis", exc)
        
def sendRequest(url, params):
    print("sendRequest: sending request to ", url, " with params", params)
    req = requests.get(url, params)
    if req.status_code != 200:
        raise Exception(f"Error thrown by the component ({req.status_code})! Chunk: {params[text]}")
    print("got response from TTS")

    return req
    
def test(url, strParams):
    print("URL: " + url)
    print("Parameters: " + strParams)
    params = json.loads(strParams)
    result = sendRequest(url, params)
    audio_bytes = BytesIO(result.content)
    print("received ", audio_bytes.getbuffer().nbytes, " bytes")
    audio, samplerate = sf.read(audio_bytes)
    print("samplerate:",samplerate)
    sf.write("./testAudio.wav", audio, samplerate=samplerate, format="wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) #, ssl_keyfile="localhost.key", ssl_certfile="localhost.crt")
