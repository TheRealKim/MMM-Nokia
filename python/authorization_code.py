"""
Example of OAuth 2.0 process with web server.
API of facebook is used: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
"""

import webbrowser
import urllib2
import json
from urllib import urlencode
from urlparse import parse_qsl, urlparse
import random
from flask import Flask, request
from threading import Thread
import threading
import time
from multiprocessing import Process, Value, Manager
import configparser, os

config = configparser.ConfigParser()

###########################
# STEP 1: user confirmation
###########################

CLIENT_KEY = '0249b9cdea0e3d37ddcbf08bc752a43c04cbfdc0d7dcdd46ebf7bbef3ebdb4ba'
CLIENT_SECRET = '0e734dd2f4d57a5ce86f6b038df5bc5cb8d5cd0978b291f4b5f53bf0756a0738'
    # host must be set explicitly in facebook app configuration, otherwise forbidden
CALLBACK_URL = "http://127.0.0.1:8080/callback"

AUTHORIZE_URL = 'https://account.health.nokia.com/oauth2_user/authorize2'
ACCESS_TOKEN_URL = 'https://account.health.nokia.com/oauth2/token'
API_RESOURCE_URL = 'https://api.health.nokia.com/v2/user?action=getdevice'

auth_params = {
    "client_id": CLIENT_KEY,
    "state": str(random.getrandbits(64)),  # to protect from CSRF
    "redirect_uri": CALLBACK_URL,
    "scope": "user.info,user.metrics,user.activity",  # we want to get access to user info, user metrics and user activity i.e. everything
    "response_type": "code",
}

url = "?".join([AUTHORIZE_URL, urlencode(auth_params)])
print url
webbrowser.open_new_tab(url)

##################################################################
# STEP 2: open flask server in other thread to accept the callback
##################################################################

killed = False
def monitoring_loop():
    while not killed:
        app = Flask(__name__)

        @app.route("/")
        def hello():
            return "Hello World!"

        @app.route("/callback")
        def callback():
            authcode = request.args.get("code")
            authstate = request.args.get("state")
            print authcode
            print authstate
            print "writing ini file"
            if not os.path.exists('authorization.ini'):
                config['authorization'] = {'authcode': authcode, 'authstate': authstate}
            config.write(open('authorization.ini', 'w'))
            return "Callback succeeded. You may now close this window"

        if __name__ == "__main__":
            app.run(host='127.0.0.1', port=8080)


server = Process(target=monitoring_loop)
server.start()

while not os.path.exists('authorization.ini'):
    time.sleep(1)
    print "waiting for response ..."
    
print "terminating server"
server.terminate()
server.join()

config.read('authorization.ini')
authcode = config.get('authorization', 'authcode')
authstate = config.get('authorization', 'authstate')
print "authorization code is: " + str(authcode)
print "authorization state is: " + str(authstate)
os.remove('authorization.ini')

######################
# STEP 3: access token
######################
access_token_params = {
    "client_id": CLIENT_KEY,
    "redirect_uri": CALLBACK_URL,
    "client_secret": CLIENT_SECRET,
    "code": authcode,
    "grant_type": "authorization_code"
}

# send POST request. Facebook and VK also ok with GET, but google only POST
resp = urllib2.urlopen(ACCESS_TOKEN_URL, data=urlencode(access_token_params))
assert resp.code == 200
resp_content = json.loads(resp.read())
access_token = resp_content['access_token']
expires_in = resp_content['expires_in']
refresh_token =resp_content['refresh_token']
user_id =resp_content['userid']
print "access_token", access_token
print "expires_in", expires_in
print "refresh_token", refresh_token
print "user_id", user_id

####################################
# STEP 4: request to server resource
####################################
api_params = {
    'access_token': access_token,
}
url = "&".join([API_RESOURCE_URL, urlencode(api_params)])
print url
resp = urllib2.urlopen(url)
assert resp.code == 200
resp_content = json.loads(resp.read())
print resp_content['body']['devices'][0]['type']
#print "Email:", email
print "All params:", resp_content