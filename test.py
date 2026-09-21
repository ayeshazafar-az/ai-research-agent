import toml
import urllib.request
import json

try:
    secrets = toml.load('.streamlit/secrets.toml')
    key = secrets.get('GROQ_API_KEY', '')
    req = urllib.request.Request('https://api.groq.com/openai/v1/models', headers={'Authorization': 'Bearer ' + key})
    response = urllib.request.urlopen(req)
    data = json.load(response)
    print("MODELS:")
    for m in data['data']: print(m['id'])
except Exception as e:
    print("Error:", e)
