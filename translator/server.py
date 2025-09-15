import os
import tempfile
import whisper
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("base")
    return whisper_model

def transcribe_audio(file_path):
    """Transcribe audio file using Whisper"""
    model = get_whisper_model()
    result = model.transcribe(file_path)
    return result["language"], result["text"].strip()

def translate_text(text, target_language):
    """Translate text using OpenAI GPT"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text to {target_language}. Only return the translated text, nothing else."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

@app.route("/translate", methods=["POST"])
def translate():
    try:
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return "No file selected", 400
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                detected_language, transcript = transcribe_audio(temp_path)
                
                target_language = request.form.get("targetLang", "en")
                
                translated_text = translate_text(transcript, target_language)
                
                return jsonify({
                    "original_language": detected_language,
                    "transcript": transcript,
                    "target_language": target_language,
                    "translated": translated_text
                })
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        elif request.is_json:
            data = request.get_json()
            text = data.get("text")
            target_language = data.get("targetLang", "en")
            
            if not text:
                return "No text provided", 400
            
            translated_text = translate_text(text, target_language)
            
            return jsonify({
                "original_text": text,
                "target_language": target_language,
                "translated": translated_text
            })
        
        else:
            return  "No file or text provided", 400
            
    except Exception as e:
        return str(e), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
