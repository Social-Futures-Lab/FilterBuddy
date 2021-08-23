# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
from os.path import realpath, join, dirname
# Find the files dynamically

CLIENT_SECRETS_FILE = realpath(join(dirname(__file__), "client_secret_youtube.json"))
DEVELOPER_KEY_FILE = realpath(join(dirname(__file__), "developer_key.txt"))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
DEVELOPER_KEY = open(DEVELOPER_KEY_FILE).read()
