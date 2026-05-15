import pika, sys, os
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def main():
  client = MongoClient("host.docker.internal", 27017)
  db_videos = client.videos
  db_mp3s = client.mp3s
  #gridfs
  fs_videos = gridfs.GridFS(db_videos)
  fs_mp3s = gridfs.GridFS(db_mp3s)

  #rabibtmq connection
  connection = pika.BlockingConnection(
    pika.ConnectionParameters(
      host="rabbitmq", 
      heartbeat=600,              
      blocked_connection_timeout=300)
  )
  channel = connection.channel()

  video_queue = os.environ.get("VIDEO_QUEUE")
  if not video_queue:
    raise RuntimeError("VIDEO_QUEUE is not configured")
  channel.queue_declare(queue=video_queue, durable=True)
  
  def callback(ch, method, properties, body):
    try:
      err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
      if err:
        print(f"Conversion failed: {err}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
      else:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as err:
      # Keep the consumer alive even if a malformed message or conversion error occurs.
      print(f"Unhandled conversion error: {err}")
      ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

  channel.basic_consume(
    queue=video_queue, on_message_callback=callback
  )

  print("Waiting messages. To exit, press control + 'C'")

  channel.start_consuming()

if __name__ == "__main__":
  try:
    main();
  except KeyboardInterrupt:
    print("Interrupted")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)      