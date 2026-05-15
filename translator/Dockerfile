FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 8080
CMD ["python3", "server.py"]
