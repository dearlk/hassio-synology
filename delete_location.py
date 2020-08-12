import requests

x = requests.delete('http://192.168.1.165:8005/api/v1/database/myhome')
print(x.text)
