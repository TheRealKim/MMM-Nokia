#!/usr/bin/env python
#I adapted this code from Geek Dad:
#(http://pdwhomeautomation.blogspot.co.uk/2015/03/using-fitbit-api-on-raspberry-pi-with.html)
import base64
import urllib 
import urllib2
import json
import os
import sys

from iniHandler import print_json, ReadCredentials, WriteTokens, ReadTokens

#Get credentials from file
client_id, client_secret = ReadCredentials()

#URL to refresh the access token
TokenURL = "https://account.health.nokia.com/oauth2/token"

#Some reponces defining API error handling responses
Authorised = "Tokens valid"
TokenRefreshedOK = "Token refreshed OK"
Reauthorise = "Invalid token, reauthorise fitbit API"
ErrorInAPI = "Error when making API call that I couldn't handle"

#Make a HTTP POST to get new tokens
def GetNewAccessToken(RefToken):
	print_json('status','Getting a new access token')
	
	#Form the data payload
	BodyText = {'grant_type' : 'refresh_token',
				'refresh_token' : RefToken}
	#URL Encode it
	BodyURLEncoded = urllib.urlencode(BodyText)
	#print "Using this as the body when getting access token >>" + BodyURLEncoded
	
	#Start the request
	tokenreq = urllib2.Request(TokenURL,BodyURLEncoded)
	
	#Add the headers, first we base64 encode the client id and client secret with a : inbetween and create the authorisation header
	tokenreq.add_header('Authorization', 'Basic ' + base64.b64encode(client_id + ":" + client_secret))
	tokenreq.add_header('Content-Type', 'application/x-www-form-urlencoded')
	
	#Fire off the request
	try:
		tokenresponse = urllib2.urlopen(tokenreq)
		
		#See what we got back. If it's this part of the code it was OK
		FullResponse = tokenresponse.read()
		
		#Use JSON to extract tokens
		ResponseJSON = json.loads(FullResponse)
		
		#Read the access token as a string
		NewAccessToken = str(ResponseJSON['access_token'])
		NewRefreshToken = str(ResponseJSON['refresh_token'])
		#print ResponseJSON['expires_at']
		#Write the access token to the ini file
		WriteTokens(NewAccessToken,NewRefreshToken)
		
		print_json('status', 'Tokens refreshed')
	except urllib2.URLError as err:
		print_json('error', 'Error getting new access token', err)
		sys.exit(1)
