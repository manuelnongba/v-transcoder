import os, gridfs, pika, json, requests
from flask import Flask, request, send_file, jsonify
from flask_pymongo import PyMongo
from auth import validate
from auth_service import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)
# server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")

mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", heartbeat=600, blocked_connection_timeout=300))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
  token, err = access.login(request)

  if not err:
    return token
  else:
    return err
  
@server.route("/upload", methods=["POST"])
def upload():
  access, err = validate.token(request)

  if err:
    return err

  access = json.loads(access)

  if access["admin"]:
    if len(request.files) < 1 or len(request.files) > 1:
      return "exactly 1 file should be uploaded", 400
    
    for _, file in request.files.items():
      err = util.upload(file, fs_videos, channel, access)

      if err:
        return err
      
      return "succes", 200
  else:
    return "not authorized"
  
@server.route("/download", methods=["GET"])
def download():
  access, err = validate.token(request)

  if err:
    return err

  access = json.loads(access)

  if access["admin"]:
    fid_str = request.args.get("fid")

    if not fid_str:
      return "fid is requires", 400
    
    try:
      out = fs_mp3s.get(ObjectId(fid_str))
      return send_file(out, download_name=f'{fid_str}.mp3')
    except Exception as err:
      return "internal server error", 500

  return "not authorized", 401

@server.route("/transcribe", methods=["POST"])
def transcribe():
  access, err = validate.token(request)

  if err:
    return err

  access = json.loads(access)

  if access["admin"]:
    if len(request.files) < 1 or len(request.files) > 1:
      return "exactly 1 file should be uploaded", 400
    
    for _, file in request.files.items():
      try:
        # Forward the file to the transcriber service
        transcriber_url = "http://transcriber-service:8080/transcribe"
        files = {"file": (file.filename, file.stream, file.content_type)}
        
        response = requests.post(transcriber_url, files=files, timeout=300)
        
        if response.status_code == 200:
          return response.json()
        else:
          return f"Transcription failed: {response.text}", response.status_code
          
      except Exception as err:
        return f"Internal server error: {str(err)}", 500
  else:
    return "not authorized", 401

@server.route("/translate", methods=["POST"])
def translate():
  access, err = validate.token(request)

  if err:
    return err

  access = json.loads(access)

  if access["admin"]:
    try:
      # Forward the request to the translator service
      translator_url = "http://translator-service:8080/translate"
      
      if request.files:
        # If file is uploaded, forward as multipart form
        files = {}
        for key, file in request.files.items():
          files[key] = (file.filename, file.stream, file.content_type)
        
        # Add form data
        data = {}
        for key, value in request.form.items():
          data[key] = value
        
        response = requests.post(translator_url, files=files, data=data, timeout=300)
      else:
        # If JSON data, forward as JSON
        response = requests.post(translator_url, json=request.get_json(), timeout=300)
      
      if response.status_code == 200:
        return response.json()
      else:
        return f"Translation failed: {response.text}", response.status_code
        
    except Exception as err:
      return f"Internal server error: {str(err)}", 500
  else:
    return "not authorized", 401


if __name__ == "__main__":
  server.run(host="0.0.0.0", port=8080)