"""
Sample Oracle NetSuite SuiteQL REST API query with OAuth1
# Azure Databricks Edition
# version 1.0 / 2025-05-17 (2025-05-17) / Alex (kinuski-dev)
"""

# from ntpath import join
import uuid
import time
import base64
import hashlib
import json
import urllib.parse
import hmac
import requests as req

# Decorations
W  = "\033[0m"  # white
R  = "\033[31m" # red
B  = "\033[34m" # blue

# Customer-specific base URL
REALM = "1234567"
BASE_URL = F"https://{REALM}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

HTTP_METHOD = "POST"
OAUTH_SIGNATURE_METHOD = "HMAC-SHA256"
OAUTH_VERSION = "1.0"
# Nonce and timestamp must be generated anew for every request
OAUTH_TIMESTAMP = round(time.time())
# Some NetSuite versions (old?) require 11-char long nonce (no hard proof; just googled it; maybe obsolete)
OAUTH_NONCE_LENGTH = 11
OAUTH_NONCE = uuid.uuid4().hex[:OAUTH_NONCE_LENGTH]
# Get secrets from the Key Vault
SECRETSCOPE = "secretscope-mykeyvault"
OAUTH_CONSUMER_KEY = dbutils.secrets.get(SECRETSCOPE, F"secret-netsuite-{REALM}-oauth1-consumer-key")
OAUTH_CONSUMER_SECRET = dbutils.secrets.get(SECRETSCOPE, F"secret-netsuite-{REALM}-oauth1-consumer-secret")
OAUTH_TOKEN_ID = dbutils.secrets.get(SECRETSCOPE, F"secret-netsuite-{REALM}-oauth1-token-id")
OAUTH_TOKEN_SECRET = dbutils.secrets.get(SECRETSCOPE, F"secret-netsuite-{REALM}-oauth1-token-secret")

# Authentication parameters
auth_params = [
    f"oauth_consumer_key={OAUTH_CONSUMER_KEY}",
    f"oauth_nonce={OAUTH_NONCE}",
    f"oauth_signature_method={OAUTH_SIGNATURE_METHOD}",
    f"oauth_timestamp={str(OAUTH_TIMESTAMP)}",
    f"oauth_token={OAUTH_TOKEN_ID}",
    f"oauth_version={OAUTH_VERSION}"
]

# Sort in alphabetical order (RFC 5849)
param_base = "&".join(str(x) for x in sorted(auth_params))

# Percent-encode all strings (RFC 3986) and concat to Signature Base
url_encoded = urllib.parse.quote_plus(BASE_URL)
param_encoded = urllib.parse.quote_plus(param_base)
signature_base = "&".join([HTTP_METHOD.upper(), url_encoded, param_encoded])

# Signature Key
signature_key = "&".join([OAUTH_CONSUMER_SECRET, OAUTH_TOKEN_SECRET])

# The signature must not contain +, = and / characters -> must be percent-encoded
digest = hmac.new(
    key=str.encode(signature_key),
    msg=str.encode(signature_base),
    digestmod=hashlib.sha256
).digest()
digest64 = base64.b64encode(digest).decode()
signature = urllib.parse.quote_plus(digest64)

# HTTP request
auth_header = 'OAuth realm="' + REALM + '",' + ','.join([
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
    "Authorization": auth_header,
    "Content": "application/json",
    "Cookie": "NS_ROUTING_VERSION=LAGGING",
    "Prefer": "transient"
}
body = {
    "q": "SELECT top 2 id, col1, col2 FROM table1"
}

response = req.request(HTTP_METHOD.upper(), F"{BASE_URL}", headers=headers, data=json.dumps(body))

if response.status_code == 200:
    print(F"{B}HTTP response code = {response.status_code}")
    payload = json.loads(response.text)
    print(F"Number of rows in the payload = {str(payload['count'])}{', and has more data' if payload['hasMore'] else ', and has no more data'}{W}\n")
    print(F"{response.text[:500]}...")

    # Convert to dataframe
    df = spark.read.json(sc.parallelize(payload["items"]))
    display(df)
else:
    print(F"{R}HTTP response code = {response.status_code}")
    print(F"{response.text}{W}")
