# V-Transcoder: Video Processing Microservices Platform

A Python microservices application for video processing, including conversion to MP3, speech-to-text transcription, and openai translation services.

## Prerequisites

- Docker
- kubectl
- minikube
- PostgreSQL (running on localhost:5432)
- MongoDB (running on localhost:27017)

Create .yaml files for the required secrets:

auth-secret → contains POSTGRES_PASSWORD, JWT_SECRET

notification-secret → contains GMAIL_ADDRESS, GMAIL_PASSWORD

openai-secret → contains OPENAI_API_KEY

Example structure:

```
apiVersion: v1
kind: Secret
metadata:
name: auth-secret
type: Opaque
stringData:
POSTGRES_PASSWORD: "your-db-password"
JWT_SECRET: "your-jwt-secret"
```

## Quick Start

1. **Start minikube:**

   ```bash
   make start-minikube
   ```

````

2. **Build images:**

   ```bash
   make build-all
   ```

3. **Deploy services:**

   ```bash
   make deploy-all
   ```

4. **Start tunnel (in another terminal):**

   ```bash
   make tunnel
   ```

5. **Add to /etc/hosts:**

   ```
   127.0.0.1 mp3converter.com
   ```

6. **Access:** http://mp3converter.com

## Services

- **Auth**: User authentication and authorization (port 5000)
- **Gateway**: Main API gateway and request routing (port 8080)
- **Converter**: Video to MP3 conversion service
- **Transcriber**: Speech-to-text transcription using Whisper AI
- **Translator**: AI-powered text translation using OpenAI GPT
- **Notification**: Email notification service
- **RabbitMQ**: Message queue for service communication
````
