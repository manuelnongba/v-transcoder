import os
import tempfile
import whisper
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

model = None

def get_whisper_model():
    global model
    if model is None:
        model = whisper.load_model("base")
    return model

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "file" not in request.files:
            return "No file provided", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            whisper_model = get_whisper_model()
            result = whisper_model.transcribe(temp_path)
            
            detected_language = result["language"]
            transcript = result["text"].strip()
            
            return jsonify({
                "language": detected_language,
                "transcript": transcript
            })
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
