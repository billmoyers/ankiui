FROM ubuntu:16.04

MAINTAINER Bill Moyers version: 0.1

RUN apt-get update
RUN apt-get install -y python3-tornado python3-decorator python3-pyaudio
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

COPY . /app
