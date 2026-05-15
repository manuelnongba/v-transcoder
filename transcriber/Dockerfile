FROM python:3.10-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential \
  ffmpeg \
  && pip install --no-cache-dir --upgrade pip "setuptools<81" wheel

WORKDIR /app
COPY ./requirements.txt /app
RUN printf "setuptools<81\n" > /tmp/constraints.txt \
  && PIP_CONSTRAINT=/tmp/constraints.txt pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 8080
CMD ["python3", "server.py"]
