-------------------------------------------------
[Tacotron2 + MelGAN] Text-to-Speech PyTorch Model
-------------------------------------------------

MODEL DESCRIPTION
-----------------
Tacotron2 + MelGAN is a combo of two deep learning parametric models that permit speech generation from text. Tacotron2 is a sequence-to-sequence model type with a classic encoder-decoder with attention structure that transforms a text sequence into a mel-scale spectrogram sequence. This mel-scale spectrogram representation is then passed by the MelGAN model (a parametric vocoder) that will transform it into a time-scale waveform sequence (synthetic speech).
Tacotron2 version provided has trained style tokens. These are embedding vectors that contain speaker style information. This style info is added to the hidden encoder output states of Taco2 in order to change prosody attributes of the output speech. 

The combo model accepts two inputs: text sequence and style tokens scores. The text input has to be set as an ordinary string, and the scores as a numpy array of 1-by-3 size (we only set 3 different scores). Note that each score should be set in the range between [0.05, 0.7] and the sum of the 3 of them should be 1 (this is a thumb-up rule to generate stable speech).

Both models have been trained with GPU's, but they can be loaded into a CPU for inference. I tested them in my own CPU (Intel Core i7-4790 CPU @ 3.60GHz x 4) and inference time oscillates between 1 to 2 seconds from text to speech.  

CUDA version used for training (Tacotron2 model with style tokens) is CUDA 9.0.176.

 
DOCKERFILE
----------
The docker image is built with Python3.6 and Tacotron2 and MelGAN projects cloned from Git repository. The requirements file is located in the Tacotron2 project directory. But torch (1.3.1+cu92) and torchvision (0.4.2+cu92) are installed before, because I specify the URL where to download it. I made it this way to install both versions with CUDA support (9.2 version). 


BUILD AND RUN INSTRUCTIONS
--------------------------
- How to buil and run this dockerfile from terminal:

(Step 0: Download the models from [here](https://github.com/rcarlini-upf/ingenious/releases/download/v0.0.1-prealpha/text2speech.resources.tar.gz) )

1) Change the directory to this: tts_docker

2) Build the image:

    $ docker build -t text2speech .

3) Run:

    $ docker run --name tts_test --rm -p 4000:80 -v ~/tts_docker/models:/models text2speech

    The -v will add to the machine directory the one that we pointed. In this case, the directory that contains models.

4) Open your browser and go to localhost:4000/text2speech


- If you want to access the root once running:

    $ docker exec -it tts_test /bin/bash   # or whatever your container name is


- To copy the wav file from container to host:

    $ docker cp tts_test:/text2speech_folder/test_speech.wav .   # or whatever your wav path is


APP.PY
------

- Change the wav path you wish to save the output speech:

    save_path = '/text2speech_folder/test_speech_cpu.wav'

- Input text sequence is defined in a variable, not as an argument. And style scores are for now fixed.

- By default, everything is set to be loaded on CPU (see map_location argument and device):

    [line 55] model.load_state_dict(torch.load(checkpoint_path, map_location='cpu')['state_dict'])  # Tacotron2 model
    [line 60] checkpoint = torch.load(vocoder_checkpoint_path, map_location='cpu')  # MelGAN model
    [line 80] sequence = torch.from_numpy(sequence).to(device='cpu', dtype=torch.int64)  # input text sequence when converted to torch

- ATTENTION! I tried with map_location="cuda:0" and device='cuda' to pass everything to GPU, but the following error appears:

    RuntimeError: Attempting to deserialize object on a CUDA device but torch.cuda.is_available() is False. If you are running on a CPU-only machine, please use torch.load with map_location=torch.device('cpu') to map your storages to the CPU.

    - 'torch.cuda.is_available()' is a flag that tells whether a NVIDIA GPU with CUDA library is available in the machine, and it says it is FALSE.

- Go to localhost:4000/ in your browser. You should see a 'Hello!' message. Then, initialization has been successful.

- Go to localhost:4000/text2speech. Text-to-speech should work and save a wav file with the synthesis in the path you specified.
