import requests

user_image = open("/volume1/photo/lalit.jpg","rb").read()
response = requests.post("http://localhost:5001/v1/vision/face/register",
files={"image":user_image},data={"userid":"lalit"}).json()
print(response)

user_image = open("/volume1/photo/jyoti.jpg","rb").read()
response = requests.post("http://localhost:5001/v1/vision/face/register",
files={"image":user_image},data={"userid":"jyoti"}).json()

print(response)

user_image = open("/volume1/photo/mom.jpg","rb").read()
response = requests.post("http://localhost:5001/v1/vision/face/register",
files={"image":user_image},data={"userid":"mom"}).json()

print(response)