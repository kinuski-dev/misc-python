# Sample Oracle NetSuite Saved Search (restlet) REST API query with OAuth1
# Azure Databricks Edition
# version 1.1.1 / 2025-05-08 (2022-08-22) / Alex (kinuski-dev)

from ntpath import join
import uuid
import time
import base64
import hashlib
import hmac
import requests as req
import urllib.parse
import json

# Decorations
W  = "\033[0m"  # white
R  = "\033[31m" # red
B  = "\033[34m" # blue

HTTP_METHOD = "GET"
OAUTH_SIGNATURE_METHOD = "HMAC-SHA256"
OAUTH_VERSION = "1.0"
# Nonce and timestamp must be generated anew for every request
OAUTH_TIMESTAMP = round(time.time())
# Some NetSuite versions (old?) require 11-char long nonce (no hard proof; just googled it; maybe obsolete)
OAUTH_NONCE_LENGTH = 11
OAUTH_NONCE = uuid.uuid4().hex[:OAUTH_NONCE_LENGTH]
# The secrets below are illustratory
OAUTH_CONSUMER_KEY = "sBr4WL8ujijEZdQpqnihiBHYMSJfHU5a"
OAUTH_CONSUMER_SECRET = "6lARbXY2GApLYYfYwE9wPKF3ljNH4qCY"
OAUTH_TOKEN_ID = "RaqxokDGxAJ7HJj2CpmO1XlFcfO242wK"
OAUTH_TOKEN_SECRET = "7BeS7BLkB8I290NK3adGFr6GymeOeDm1"

# Customer-specific URI
REALM = "1234567"
BASE_URI = F"https://{REALM}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"

# API request parameters
uriParamsDict = {
    "deploy": "1",
    "script": "1341",
    "searchname": "3750",
    "start": "0",
    "dateFrom": "2022/09/01"
}
# Build the parameter string for the API request
uriParamsStr = "&".join(k + "=" + v for k, v in uriParamsDict.items())

# Encode URI parameters values (e.g., the date includes "/" - must be encoded; RFC 3986)
uriParamsArray = []
for k, v in uriParamsDict.items():
    uriParamsArray.append(F"{k}={urllib.parse.quote_plus(v)}")

# Authentication parameters
authParams = [
    f"oauth_consumer_key={OAUTH_CONSUMER_KEY}",
    f"oauth_nonce={OAUTH_NONCE}",
    f"oauth_signature_method={OAUTH_SIGNATURE_METHOD}",
    f"oauth_timestamp={str(OAUTH_TIMESTAMP)}",
    f"oauth_token={OAUTH_TOKEN_ID}",
    f"oauth_version={OAUTH_VERSION}"
]

# Merge the two arrays together, sort in alphabetical order (RFC 5849), concat to signature parameter string
allParams = [*authParams, *uriParamsArray]
paramBase = "&".join(str(x) for x in sorted(allParams))

# Percent-encode all strings (RFC 3986) and concat to Signature Base
uriEncoded = urllib.parse.quote_plus(BASE_URI)
paramEncoded = urllib.parse.quote_plus(paramBase)
signatureBase = "&".join([HTTP_METHOD.upper(), uriEncoded, paramEncoded])

# Signature Key
signatureKey = "&".join([OAUTH_CONSUMER_SECRET, OAUTH_TOKEN_SECRET])

# The signature must not contain + and = characters -> must be percent-encoded
digest = hmac.new(key=str.encode(signatureKey), msg=str.encode(signatureBase), digestmod=hashlib.sha256).digest()
digest64 = base64.b64encode(digest).decode()
signature = urllib.parse.quote_plus(digest64)

# HTTP request
authHeader = 'OAuth realm="' + REALM + '",' + ','.join([
                'oauth_consumer_key="' + OAUTH_CONSUMER_KEY + '"',
                'oauth_nonce="' + OAUTH_NONCE + '"',
                'oauth_signature_method="' + OAUTH_SIGNATURE_METHOD + '"',
                'oauth_timestamp="' + str(OAUTH_TIMESTAMP) + '"',
                'oauth_token="' + OAUTH_TOKEN_ID + '"',
                'oauth_version="' + OAUTH_VERSION + '"',
                'oauth_signature="' + signature + '"'
            ])
headers = {
    "Accept": "application/json",
    "Authorization": authHeader,
    "Cookie": "NS_ROUTING_VERSION=LAGGING"
}

response = req.request(HTTP_METHOD.upper(), F"{BASE_URI}?{uriParamsStr}", headers=headers)

if response.status_code == 200:
    print(F"{B}HTTP response code = {response.status_code}")
    payload = json.loads(response.text)
    print(F"Number of rows in the payload = {str(len(payload['lines']))}")
    print(F"There is more data available  = {str(payload['more'])}{W}\n")
    print(F"{response.text[:500]}...")
else:
    print(F"{R}HTTP response code = {response.status_code}")
    print(F"{response.text}{W}")
