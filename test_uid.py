import requests

url = "http://127.0.0.1:5000/uid"
data = {"uid": "123456"}

response = requests.post(url, json=data)
print("Server responded with:", response.text)
