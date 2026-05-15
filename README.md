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

- Auth: User authentication and authorization (port 5000)
- Gateway: Main API gateway and request routing (port 8080)
- Converter: Video to MP3 conversion service
- Transcriber: Speech-to-text transcription using Whisper AI
- Translator: AI-powered text translation using OpenAI GPT
- Notification: Email notification service
- RabbitMQ: Message queue for service communication

## Troubleshooting

### `kubectl apply` fails with OpenAPI connection refused

Error example:

`failed to download openapi ... connect: connection refused`

Cause: `kubectl` points to a stopped Minikube API server.

Fix:

```bash
minikube status
make start
```

Then re-run deploy:

```bash
make deploy-all
```

### `pika.exceptions.AMQPConnectionError`

Cause: RabbitMQ is not ready (often because its PVC was missing or pending).

Checks:

```bash
kubectl get pod rabbitmq-0
kubectl describe pod rabbitmq-0
kubectl get pvc
```

If needed, re-apply RabbitMQ manifests:

```bash
kubectl apply -f rabbit/manifest/
```

### `pika.exceptions.ChannelClosedByBroker: (404, "NOT_FOUND - no queue 'video' ...")`

Cause: producers/consumers connected before queues existed.

Fix now included in code: services declare durable `video` and `mp3` queues at startup/publish time.

### `http://rabbitmq-manager.com` not working

Checks/fix:

```bash
minikube addons enable ingress
make tunnel
```

Ensure hosts mapping includes:

`127.0.0.1 rabbitmq-manager.com`
