import glob
import json
import requests

IP = "192.168.1.165"
PORT = "32769"
lalit_dir = "C:\\lalit\\"
jyoti_dir = "C:\\jyoti\\"
TIMEOUT = 60 # seconds for a request

def process_image(file_path: str, userid: str):
    """
    Process an image with deepstack.
    """
    try:
        user_image = open(file_path, "rb").read()
        response = requests.post("http://{}:{}/v1/vision/face/register".format(IP,PORT),files={"image":user_image},data={"userid":userid}).json()
        print(response)
    except Exception as exc:
        print(exc)

lalit_files = glob.glob(lalit_dir + "*.jpg")
for file in lalit_files:
    print(file)
    process_image(file,"lalit")

jyoti_files = glob.glob(jyoti_dir + "*.jpg")
for file in jyoti_files:
    print(file)
    process_image(file,"jyoti")
