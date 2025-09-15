import requests, os

def transcribe(request):
  if len(request.files) < 1 or len(request.files) > 1:
      return "exactly 1 file should be uploaded", 400
    
  for _, file in request.files.items():
    try:
      transcriber_url = f"http://{os.environ.get('TRANSCRIBER_SERVICE_ADDRESS')}/transcribe"
      files = {"file": (file.filename, file.stream, file.content_type)}
      
      response = requests.post(transcriber_url, files=files, timeout=300)
      
      if response.status_code == 200:
        return response.json(), None
      else:
        return None, (f"Transcription failed: {response.text}", response.status_code)
        
    except Exception as err:
      return None, (f"Internal server error: {str(err)}", 500)
