import os, gridfs, pika, json
from flask import Flask, request, send_file
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

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
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


if __name__ == "__main__":
  server.run(host="0.0.0.0", port=8080)