FROM ubuntu:20.04

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && apt-get install -y --no-install-recommends python3-pip \
    && apt update && apt install -y libsm6 libxext6 \
    && apt-get install -y libxrender-dev \
    && apt-get -y install xterm

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y gnupg2 ca-certificates \
            git build-essential libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
      && apt-get install --no-install-recommends --no-install-suggests -y libopencv-highgui4.2 \
      && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

EXPOSE 4040


CMD ["python3", "detect.py"]