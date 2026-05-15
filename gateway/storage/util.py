import pika, json, os

def upload(file, fs, channel, access):
  video_queue = os.environ.get("VIDEO_QUEUE", "video")

  try:
    file_id = fs.put(file)
  except Exception as err:
    print(err, flush=True)
    return "Internal server error", 500
  
  message = {
    "video_fid": str(file_id),
    "mp3_id": None,
    "username": access['username']
  }

  try:
    channel.basic_publish(
      exchange="",
      routing_key=video_queue, #routing_key is the queue
      body=json.dumps(message),
      properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
      )
    )
  except Exception as err:
    print(err, flush=True)
    fs.delete(file_id)
    return "Internal server error", 500