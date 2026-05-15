# V-Transcoder: Video Processing Microservices Platform

A Python microservices application for video processing, including conversion to MP3, speech-to-text transcription, and OpenAI translation services.

## Prerequisites

- Docker
- kubectl
- minikube
- PostgreSQL (running on localhost:5432)
- MongoDB (running on localhost:27017)

Create/update Kubernetes secrets for the required credentials:

- `auth-secret`: `POSTGRES_PASSWORD`, `JWT_SECRET`
- `notification-secret`: `GMAIL_ADDRESS`, `GMAIL_PASSWORD`
- `openai-secret`: `OPENAI_API_KEY`

Example:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: 'your-db-password'
  JWT_SECRET: 'your-jwt-secret'
```

## Quick Start

1. Start Minikube:

   ```bash
   make start
   ```

2. Enable ingress addon (required for host-based URLs):

   ```bash
   minikube addons enable ingress
   ```

3. Build images:

   ```bash
   make build-all
   ```

4. Deploy services:

   ```bash
   make deploy-all
   ```

5. Start tunnel (in another terminal):

   ```bash
   make tunnel
   ```

6. Add local host mappings:

   ```
   127.0.0.1 mp3converter.com rabbitmq-manager.com
   ```

7. Access:

- Gateway: http://mp3converter.com
- RabbitMQ Management: http://rabbitmq-manager.com

## Services

All API requests go through the gateway at `http://mp3converter.com`.

Get a JWT token first:

```bash
TOKEN=$(curl -sS -X POST http://mp3converter.com/login \
   -u "you@example.com:your-password")

echo "Token length: ${#TOKEN}"
```

- Auth: User authentication and authorization (port 5000)

```bash
curl -i -X POST http://mp3converter.com/login \
   -u "you@example.com:your-password"
```

- Gateway: Main API gateway and request routing (port 8080)

```bash
curl -i http://mp3converter.com/
```

- Converter: Video to MP3 conversion service

```bash
curl -i -X POST http://mp3converter.com/upload \
   -H "Authorization: Bearer $TOKEN" \
   -F "file=@/path/to/video-file"
```

- Transcriber: Speech-to-text transcription service

```bash
curl -i -X POST http://mp3converter.com/transcribe \
   -H "Authorization: Bearer $TOKEN" \
   -F "file=@/path/to/audio-or-video-file"
```

- Translator: AI-powered text translation using OpenAI GPT

```bash
curl -i -X POST http://mp3converter.com/translate \
   -H "Authorization: Bearer $TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"text":"Hello world","targetLang":"fr"}'
```

```bash
curl -i -X POST http://mp3converter.com/translate \
   -H "Authorization: Bearer $TOKEN" \
   -F "file=@/path/to/audio-or-video-file" \
   -F "targetLang=fr"
```

- Notification: Email notification service
  Triggered asynchronously after successful conversion; no direct gateway endpoint.

- RabbitMQ: Message queue for service communication
  Access management UI at `http://rabbitmq-manager.com`.

Download converted MP3 by file id:

```bash
curl -i -X GET "http://mp3converter.com/download?fid=<MP3_FILE_ID>" \
   -H "Authorization: Bearer $TOKEN" \
   -o output.mp3
```
