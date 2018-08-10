#!/usr/bin/env python
#I adapted this code from Geek Dad:
#(http://pdwhomeautomation.blogspot.co.uk/2015/03/using-fitbit-api-on-raspberry-pi-with.html)
import base64
from urllib import urlencode 
import urllib2
import json
import os
import sys

from iniHandler import print_json, ReadCredentials, WriteTokens, ReadTokens

#Some reponces defining API error handling responses
Authorised = "Tokens valid"
TokenRefreshedOK = "Token refreshed OK"
Reauthorise = "Invalid token, reauthorise fitbit API"
ErrorInAPI = "Error when making API call that I couldn't handle"

#Make a HTTP POST to get new tokens
def GetNewAccessToken(RefToken):

	TokenURL = "https://account.health.nokia.com/oauth2/token"
	client_id, client_secret = ReadCredentials()
	print_json('status','Getting a new access token')
	
	#Start forming the request

	refresh_token_params = {
		'grant_type': 'refresh_token',
		'client_id': client_id,
		'client_secret': client_secret,
		'refresh_token': RefToken	
    }
	
	print_json('status', 'Refreshing tokens')
	
	#Fire off the request
	try:
		tokenresponse = urllib2.urlopen(TokenURL, data=urlencode(refresh_token_params))
		assert tokenresponse.code == 200
		resp_content = json.loads(tokenresponse.read())
		
		#Read the access token as a string
		NewAccessToken = resp_content['access_token']
		NewRefreshToken =resp_content['refresh_token']
		#print ResponseJSON['expires_at']
		#Write the access token to the ini file
		WriteTokens(NewAccessToken,NewRefreshToken)
		
		print_json('status', 'Tokens refreshed')
	except urllib2.URLError as err:
		print_json('error', 'Error getting new access token', err)
		sys.exit(1)




#############
#For testing#
#############

#refresh_token = ReadTokens()[1]
#GetNewAccessToken(refresh_token)
