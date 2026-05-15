import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSCRIBER_SERVICE_ADDRESS = os.getenv("TRANSCRIBER_SERVICE_ADDRESS", "transcriber-service:8080")
TRANSCRIBER_TIMEOUT_SECONDS = int(os.getenv("TRANSCRIBER_TIMEOUT_SECONDS", "120"))
OPENAI_TIMEOUT_SECONDS = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "90"))


class TranslationError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code


def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code

def transcribe_audio(file):
    """Transcribe audio by forwarding the upload to the transcriber service."""
    transcriber_url = f"http://{TRANSCRIBER_SERVICE_ADDRESS}/transcribe"
    file.stream.seek(0)
    files = {
        "file": (
            file.filename,
            file.stream,
            file.content_type or "application/octet-stream",
        )
    }
    try:
        response = requests.post(transcriber_url, files=files, timeout=TRANSCRIBER_TIMEOUT_SECONDS)
    except requests.Timeout:
        raise TranslationError("Transcription service timed out", 504)
    except requests.RequestException:
        raise TranslationError("Unable to reach transcription service", 502)

    if response.status_code != 200:
        details = response.text.strip() if response.text else "transcriber returned an error"
        raise TranslationError(f"Transcription failed: {details}", response.status_code)

    payload = response.json()
    transcript = (payload.get("transcript") or "").strip()
    if not transcript:
        raise TranslationError("Transcription response missing transcript", 502)

    return payload.get("language"), transcript


def translate_text(text, target_language):
    """Translate text using OpenAI GPT"""
    if not OPENAI_API_KEY:
        raise TranslationError("OPENAI_API_KEY is not configured", 500)

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
            temperature=0.3,
            timeout=OPENAI_TIMEOUT_SECONDS,
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        raise TranslationError("OpenAI quota exceeded. Check billing/quota for the configured API key.", 429)
    except openai.AuthenticationError:
        raise TranslationError("OpenAI authentication failed. Verify OPENAI_API_KEY.", 401)
    except openai.BadRequestError as e:
        raise TranslationError(f"Invalid translation request: {str(e)}", 400)
    except openai.APITimeoutError:
        raise TranslationError("OpenAI request timed out", 504)
    except openai.APIConnectionError:
        raise TranslationError("Unable to connect to OpenAI API", 502)
    except openai.APIStatusError as e:
        status_code = getattr(e, "status_code", 502) or 502
        raise TranslationError(f"OpenAI API error: {str(e)}", status_code)
    except Exception as e:
        raise TranslationError(f"Translation failed: {str(e)}", 500)


@app.route("/translate", methods=["POST"])
def translate():
    try:
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return error_response("No file selected", 400)

            detected_language, transcript = transcribe_audio(file)

            target_language = request.form.get("targetLang", "en")

            translated_text = translate_text(transcript, target_language)

            return jsonify({
                "original_language": detected_language,
                "transcript": transcript,
                "target_language": target_language,
                "translated": translated_text
            })

        elif request.is_json:
            data = request.get_json(silent=True) or {}
            text = data.get("text")
            target_language = data.get("targetLang", "en")

            if not text:
                return error_response("No text provided", 400)

            translated_text = translate_text(text, target_language)

            return jsonify({
                "original_text": text,
                "target_language": target_language,
                "translated": translated_text
            })

        else:
            return error_response("No file or text provided", 400)

    except TranslationError as e:
        return error_response(str(e), e.status_code)
    except Exception as e:
        return error_response(f"Unexpected translator error: {str(e)}", 500)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
