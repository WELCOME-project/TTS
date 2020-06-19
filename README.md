DOCKERFILE
----------
The docker image is built with Python3.6 and Tacotron2 and MelGAN projects cloned from Git repository. The requirements file is located in the Tacotron2 project directory. But torch (1.3.1+cu92) and torchvision (0.4.2+cu92) are installed before, because I specify the URL where to download it. I made it this way to install both versions with CUDA support (9.2 version). 


BUILD AND RUN INSTRUCTIONS
--------------------------
- How to buil and run this dockerfile from terminal:

(Step 0: Download the models from [here](https://github.com/rcarlini-upf/ingenious/releases/download/v0.0.1-prealpha/text2speech.resources.tar.gz) )

With docker-compose:  
1) Run `docker-compose build text2speech`  
2) Run `docker-compose up text2speech` (it expects to have a directory models inside this project directory)
3) You'll find the synthesizer in this [url](http://localhost:4300/text2speech?text=This%20is%20the%20url%20of%20the%20synthesizer)

With docker:
1) Build the image: `docker build -t text2speech .`  
2) Run `docker run --name tts_test --rm -p 4000:80 -v ./models:/models text2speech`  
3) You'll find the synthesizer in this [url](http://localhost:4000/text2speech?text=This%20is%20the%20url%20of%20the%20synthesizer)

- If you want to access the root once run  `docker exec -it tts_test /bin/bash`

