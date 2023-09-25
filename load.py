import requests

url = 'http://localhost:5000/upload'
files = {'file': open('sample.csv', 'rb')}

response = requests.post(url, files=files)

if response.status_code == 201:
    print('File uploaded successfully')
else:
    print('Error:', response.status_code)
    print(response.json())