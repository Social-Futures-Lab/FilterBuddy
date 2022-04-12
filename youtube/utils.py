# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
from pathlib import Path
import googleapiclient, dateutil
from .models import Channel, RuleCollection, RuleColTemplate, Rule, Video, Comment
import sys

# Find the files dynamically
BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = Path(BASE_DIR, "client_secret_youtube.json")
DEVELOPER_KEY_FILE = Path(BASE_DIR, "developer_key.txt")

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

if DEVELOPER_KEY_FILE.is_file():
  DEVELOPER_KEY = open(DEVELOPER_KEY_FILE).read()
else:
  print('No developer key found. Using fake replacement', file=sys.stderr)
  DEVELOPER_KEY = 'THERE_IS_NO_DEVELOPER_KEY_LOADED'


def getChannel(credentials):
  youtube = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, credentials=credentials)

  channels = youtube.channels().list(mine=True, part='snippet').execute()
  if not 'items' in channels:
    return None
  for channel in channels['items']:
    channel['snippet']['publishedAt'] = dateutil.parser.parse(channel['snippet']['publishedAt'])
  myChannel = channels['items'][0]

  djangoChannel, created = Channel.objects.get_or_create(
    title=myChannel['snippet']['title'],
    description=myChannel['snippet']['description'],
    pub_date=myChannel['snippet']['publishedAt'],
    channel_id=myChannel['id'])
  return djangoChannel

def getChannelFromRequest(request):
  if 'credentials' in request.session and 'myChannelId' in request.session['credentials']:
    myChannelId = request.session['credentials']['myChannelId']
    print(myChannelId)
    myChannel = Channel.objects.get(channel_id = myChannelId)
    return myChannel
  else:
    #return makeDebugChannel()
    raise Exception('Could not get login credentials')
