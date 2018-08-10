from authHandler import GetNewAccessToken
from iniHandler import print_json, ReadTokens
import urllib
import urllib2
import json
import os
import sys

UserUrl = "https://api.health.nokia.com/v2/user?action=getdevice"
MeasureUrl = "https://api.health.nokia.com/measure?action=getmeas"
SleepUrl = "https://api.health.nokia.com/v2/sleep?action=get"

access_token, refresh_token = ReadTokens()

#Some reponces defining API error handling responses
Authorised = "Tokens valid"
TokenRefreshedOK = "Token refreshed OK"
Reauthorise = "Invalid token, reauthorise fitbit API"
ErrorInAPI = "Error when making API call that I couldn't handle"

#This makes an API call. It also catches errors and tries to deal with them
def MakeAPICall(InURL,AccToken, RefToken):
	#Start forming the request
    api_params = {
        'access_token': AccToken,
    }
    url = "&".join([InURL, urllib.urlencode(api_params)])

    print_json('status', 'Making API call')
	
	#Fire off the request
    try:
		response = urllib2.urlopen(url)
		#Read the response
		FullResponse = response.read()
		print_json('status', FullResponse)
		#Return values for successful request, tokens good, and the data recieved
		print_json('status', 'API call okay')
		return True, True, Authorised
	#Catch errors, e.g. A 401 error that signifies the need for a new access token
    except urllib2.HTTPError as err:
		HTTPErrorMessage = err.read()
		print_json('error', err, json.loads(HTTPErrorMessage))
		#See what the error was
		if (err.code == 401) and (HTTPErrorMessage.find("expired_token") > 0):
			GetNewAccessToken(RefToken, )
			print_json('status', 'Can run again')
			return False, True, TokenRefreshedOK
		if (err.code == 401) and (HTTPErrorMessage.find("invalid_token") > 0):
			return False, False, Reauthorise
		#Return that this didn't work, allowing the calling function to handle it
		print_json('status', 'API call failed')
		return False, False, ErrorInAPI


########
# USER #
########

def UserApi():
    MakeAPICall(UserUrl, access_token, refresh_token)

UserApi()