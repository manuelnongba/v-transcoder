import pika, sys, os, time
from send import email

def main():
  #rabibtmq connection
  connection = pika.BlockingConnection(
    pika.ConnectionParameters(
      host="rabbitmq",
      heartbeat=600,
      blocked_connection_timeout=300
      )
  )
  channel = connection.channel()
  mp3_queue = os.environ.get("MP3_QUEUE")
  if not mp3_queue:
    raise RuntimeError("MP3_QUEUE is not configured")
  channel.queue_declare(queue=mp3_queue, durable=True)

  def callback(ch, method, properties, body):
    err = email.notification(body)
    if err:
      ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
      ch.basic_ack(delivery_tag=method.delivery_tag)

  channel.basic_consume(
    queue=mp3_queue, on_message_callback=callback
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