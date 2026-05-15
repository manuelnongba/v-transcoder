import os
import subprocess
import tempfile
import threading
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import whisper
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

_model = None
_model_lock = threading.Lock()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")


def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = whisper.load_model(WHISPER_MODEL)
    return _model


def _save_upload_to_temp(file_storage):
    extension = Path(file_storage.filename or "").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as uploaded_file:
        file_storage.save(uploaded_file.name)
        return uploaded_file.name


def _normalize_audio_to_wav(input_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
        output_path = wav_file.name

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise RuntimeError(f"ffmpeg failed: {process.stderr.strip()}")
    return output_path

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "file" not in request.files:
            return "No file provided", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        uploaded_path = _save_upload_to_temp(file)
        wav_path = _normalize_audio_to_wav(uploaded_path)
        
        try:
            model = get_model()
            result = model.transcribe(wav_path, fp16=False)
            
            detected_language = result["language"]
            transcript = result["text"].strip()
            
            return jsonify({
                "language": detected_language,
                "transcript": transcript
            })
            
        finally:
            if os.path.exists(uploaded_path):
                os.unlink(uploaded_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
