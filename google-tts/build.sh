#!/bin/bash

tag=$(date -I)
export TAG=$tag

docker build . -t maven-taln.upf.edu/google-tts:${TAG}
docker push maven-taln.upf.edu/google-tts:${TAG}