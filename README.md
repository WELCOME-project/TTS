# TTS - Text to Speech

## Introduction

The software in this repository serves to provide Text-to-speech services. The TTS software consists of 2 submodules included here, the TTS wrapper (`tts-wrapper`) used to direct incoming requests to different underlying TTS services and voices, and an abstraction layer over Google TTS (`google-tts`) which makes it usable through the TTS wrapper (alongside other TTS systems. These submodules are publicly available on GitHub at https://github.com/WELCOME-project/TTS.

## Installation, Deployment, and Execution

### Installation and Deployment

#### Software Requirements

The WELCOME TTS installation requires the use of Docker and Docker Compose. Docker is used to package TTS as an image that can be run in a container. The `.yml` configuration file and Docker Compose are used to instantiate Docker images as containers. The `.yml` file specifies the virtual network details and other necessary configurations.

#### Hardware Requirements

The TTS wrapper image requires approximately of 100 MB of memory to run. It can utilize multiple threads, so having several CPU cores available is preferred. In the example configuration provided below, up to 4 CPU cores are used.

#### Deployment

The configuration of the tts-wrapper deployment is specified in the `.yml` file. One can use an existing image by specifying its name and tag in the `.yml` file to run the `tts-wrapper` container. The procedure is identical for the `google-tts` container

To create the image from scratch, access the project directory and run the command:
```
docker build -f Dockerfile -t name_of_the_image:tag .
```
Then upload it to a Maven repository with the command:
```
docker push name_of_the_image:tag
```
Use this image inside the `.yml` file.

The `tts-wrapper` needs to be configured to point to the correct TTS service for each language code, which is done in `tts-wrapper/app/language_config.json`. The provided example points to non-public URLs for these services and would therefore need to be adjusted accordingly.

The `google-tts` container requires credentials to access Google's TTS services, which need to be provided in a file which is referenced by the `OOGLE_APPLICATION_CREDENTIALS` variable. This file can e.g. be provided via a bind mount or similar mechanism.

#### Example `compose.yml` for Deployment

Here is an example `compose.yml` file that can be used for deployment, which includes the tts-wrapper and google-tts services. Adjust the image tag and port mapping as required:

```
version: '3.2'
services:
  tts-wrapper:
    image: maven-taln.upf.edu/welcome/tts-wrapper:2023-03-28
    volumes:
      - /resources/projects/welcome/tts_cache:/cache
    environment: 
      - CACHE_DIR=/cache/
    deploy:
      replicas: 1
      resources:
        limits:
            cpus: "4"
            memory: 1GB
    ports:
      - "8001:80"
  google-tts:
    image: maven-taln.upf.edu/google-tts:2022-06-30
    volumes:
      - /resources/projects/welcome/google-credentials.json:/google-credentials.json
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/google-credentials.json
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "4"
          memory: 1GB      
      ports:
        - "8002:80"
```

### Execution

The deployed TTS component can run in the cloud infrastructure of the installed WELCOME platform or be deployed externally. Make the corresponding adjustments in the dispatcher configuration to point to the appropriate service URL.

The service is accessible through a REST-like API at `http://<base_url>/` where `<base_url>` corresponds to the location of the deployment. For example, `http://tts-wrapper:80/` or `https://welcome-project.upf.edu/tts-wrapper/` (with a corresponding proxy configuration). Swagger documentation is available at that endpoint. The `google-tts` service does not need to be exposed directly as it can be accessed through the `tts-wrapper` according to the language configuration.
