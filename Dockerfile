# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

# Install locales package
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/*

# Set the locale to German (UTF-8)
RUN sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=de_DE.UTF-8

ENV LANG de_DE.UTF-8
ENV LC_ALL de_DE.UTF-8

COPY . .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP app.py

ENTRYPOINT ["python", "-m", "flask", "--debug", "run", "--host=0.0.0.0"]
