from io import BytesIO
import socket

import requests
from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

import t2s_pipeline as pl 

app = FastAPI()

def create_pipeline():

    logger.info("Loading T2S pipeline...")

    tacotron_model_path = "/models/checkpoint_7800.model"
    vocoder_model_path = "/models/nvidia_tacotron2_LJ11_epoch6400.pt"

    config = pl.T2SPipelineConfiguration()
    t2s_pipeline = pl.T2SPipeline(tacotron_model_path, vocoder_model_path, config)

    logger.info("T2S pipeline loaded successfully!")

    return t2s_pipeline

pipeline = create_pipeline()

@app.get("/")
def hello():
    html = "<h3>TTS</h3>" \
           "<b>Hostname:</b> {hostname}<br/>"

    return html.format(hostname=socket.gethostname())


@app.get(
    "/text2speech",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "Return the generated audio in wav format.",
        }
    }    
    )
def text2speech(text:str = None):
    global pipeline

    if text:
        logger.info("Processing text...")

        # scores=[0.58, 0.12, 0.3]
        output = BytesIO()
        pipeline.process(text, output)

        logger.info("Text processed!")

        return StreamingResponse(output, headers={'Content-Disposition': 'attachment; filename=audio.wav'}, media_type='audio/wav')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
