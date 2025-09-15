import requests, os

def translate(request):
  try:
    translator_url = f"http://{os.environ.get('TRANSLATOR_SERVICE_ADDRESS')}/translate"
    
    if request.files:
      
      files = {}
      for key, file in request.files.items():
        files[key] = (file.filename, file.stream, file.content_type)
      
      
      data = {}
      for key, value in request.form.items():
        data[key] = value
      
      response = requests.post(translator_url, files=files, data=data, timeout=300)
    else:
      
      response = requests.post(translator_url, json=request.get_json(), timeout=300)
    
    if response.status_code == 200:
      return response.json(), None
    else:
      return None, (f"Translation failed: {response.text}", response.status_code)
  except Exception as err:
    return None, (f"Internal server error: {str(err)}", 500)