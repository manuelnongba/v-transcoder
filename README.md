# Video to MP3 Converter Microservices

A Python microservices application that converts videos to MP3 format.

## Prerequisites

- Docker
- kubectl
- minikube
- PostgreSQL (running on localhost:5432)
- MongoDB (running on localhost:27017)

## Quick Start

1. **Start minikube:**

   ```bash
   make start-minikube
   ```

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

- **Auth**: User authentication (port 5000)
- **Gateway**: Main API gateway (port 8080)
- **Converter**: Video to MP3 conversion
- **Notification**: Email notifications
- **RabbitMQ**: Message queue
