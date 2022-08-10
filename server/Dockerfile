FROM python:3.9

USER root

RUN pip install --upgrade pip
WORKDIR /code
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

EXPOSE 8000


CMD ["python3", "main.py"]