
import requests, xmltodict, sys

## Set Motion Config:
## http://192.168.2.50:88/cgi-bin/CGIProxy.fcgi?cmd=setMotionDetectConfig&isEnable=1&usr=admin&pwd=PASSWORD&linkage=0&snapInterval=3&&sensitivity=1&triggerInterval=0&schedule0=281474976710655&schedule1=281474976710655&schedule2=281474976710655&schedule3=281474976710655&schedule4=281474976710655&schedule5=281474976710655&schedule6=281474976710655&area0=1023&area1=1023&area2=1023&area3=1023&area4=1023&area5=1023&area6=1023&area7=1023&area8=1023&area9=1023
## Get Motion Status:
## http://192.168.2.50:88/cgi-bin/CGIProxy.fcgi?cmd=getMotionDetectConfig&isEnable=1&usr=admin&pwd=PASSWORD
## Get Motion Alert:
## Example URL: http://192.168.2.52:88/cgi-bin/CGIProxy.fcgi?cmd=getDevState&isEnable=1&usr=admin&pwd=PASSWORD

def getMotionAlert(ip, usr, pwd):
	url = "http://%s:88/cgi-bin/CGIProxy.fcgi?cmd=getDevState&usr=%s&pwd=%s" % (ip,usr,pwd)
	response = requests.get(url)
	doc = xmltodict.parse(response.content)
	result = doc['CGI_Result']['motionDetectAlarm'][0]
	
	# 0-Disabled, 1-No Alarm, 2-Detect Alarm
	print(result)
	
def getMotionStatus(ip, usr, pwd):
	url = "http://%s:88/cgi-bin/CGIProxy.fcgi?cmd=getMotionDetectConfig&usr=%s&pwd=%s" %(ip,usr,pwd)
	response = requests.get(url)
	doc = xmltodict.parse(response.content)
	result = doc['CGI_Result']['isEnable'][0]
	print(result)

def setMotionStatus(ip, usr, pwd, enabled):
	url = "http://%s:88/cgi-bin/CGIProxy.fcgi?cmd=setMotionDetectConfig&usr=%s&pwd=%s&isEnable=%s" %(ip,usr,pwd,enabled)
	url = url + "&linkage=0&snapInterval=3&&sensitivity=1&triggerInterval=0&schedule0=281474976710655&schedule1=281474976710655&schedule2=281474976710655&schedule3=281474976710655&schedule4=281474976710655&schedule5=281474976710655&schedule6=281474976710655&area0=1023&area1=1023&area2=1023&area3=1023&area4=1023&area5=1023&area6=1023&area7=1023&area8=1023&area9=1023"
	response = requests.get(url)
	doc = xmltodict.parse(response.content)
	result = doc['CGI_Result']['result'][0]
	print(result)
	
def ptzGotoPresetPoint(ip, usr, pwd, preset):
	url = "http://%s:88/cgi-bin/CGIProxy.fcgi?cmd=ptzGotoPresetPoint&usr=%s&pwd=%s&name=%s" %(ip,usr,pwd,preset)
	response = requests.get(url)
	doc = xmltodict.parse(response.content)
	result = doc['CGI_Result']['runResult'][0]
	# 0-Success, 1-Error
	print(result)


if __name__ == "__main__":
	func = sys.argv[1]
	
	if func == "getMotionAlert":
		getMotionAlert(sys.argv[2], sys.argv[3], sys.argv[4])
	elif func == "getMotionStatus":
		getMotionStatus(sys.argv[2], sys.argv[3], sys.argv[4])
	elif func == "setMotionStatus":
		setMotionStatus(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
	elif func == "ptzGotoPresetPoint":
		ptzGotoPresetPoint(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
	else:
		print("Add Function to Main!!!!")