from flask import json
import ipaddress, sys, base64
import google.cloud.logging, google.auth

#from httplib2 import Credentials, Http
#from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

import logging

SCOPES = ['https://www.googleapis.com/auth/chat.bot']
# When running in Cloud Function, we're using ADC:
CREDENTIALS, project = google.auth.default(scopes=SCOPES)

usage = """

*Usage:*

  @Subnet Calculator range <aa.bb.cc.dd/mm> - _show range of IPs represented by Subnet_

"""

def on_event(psmessage, context):
  """ Handles an event from Google Chat.
  
  Args:
      psmessage: message from pub/sub
      context: pub/sub trigger of Cloud Function context
  
  """
  
  event = json.loads( base64.b64decode(psmessage['data']).decode('utf-8') )
  logging.info(f'event = {event}')

  if event['type'] == 'ADDED_TO_SPACE':
    thread = event['message']['thread']['name'] if 'message' in event else ''
    resp = 'Thanks for adding me to "%s"!\n' % (event['space']['displayName'] if 'displayName' in event['space'] else 'this chat')
    resp += usage
  elif event['type'] == 'MESSAGE':
    thread = event['message']['thread']['name']
    resp = do_subnetcalc(' '.join ( event['message']['text'].split()[2:] ) )
  elif event['type'] == 'REMOVED_FROM_SPACE':
    return
  else:
    # Something weird has happened
    logging.error("Received unexpected event type/format from pub/sub")
    return

  send_text_to_chat(resp, thread)
  #return json.jsonify({'text': resp})

def do_subnetcalc(event_message):
  """ Carries out IP subnet calculation based on command and arguments requested

  Args:
      event_message: user's command and arguments text
  
  """

  arguments = event_message.lower().split()
  # print(len(arguments))

  if len(arguments) == 0:
    return usage
  
  elif arguments[0] == 'range':
    if len(arguments) > 1:
      return calc_ip_range(arguments[1])
    else:
      return "No CIDR parameter specified\n" + usage
  
  #elif arguments[0] == all the other great commands we'll get round to implementing
  
  else:
    return "Unrecognised command: %s" % arguments[0]
  

def calc_ip_range(cidr_text):
  try:
    cidr_block = ipaddress.ip_network(cidr_text)
  except ValueError as e:
    #print(e)
    return "Invalid Subnet: %s" % e

  return "*" + cidr_text.replace("/", " /") + ":* " + \
    str(cidr_block[0]) + " - " + str(cidr_block[cidr_block.num_addresses - 1]) + \
    " (Usable addresses: " + str(cidr_block[1]) + " - " + str(cidr_block[cidr_block.num_addresses - 2]) + ")"

def send_text_to_chat(text, thread):
  try:
    chat = build('chat', 'v1', credentials=CREDENTIALS)
    #logging.info(f'Sending to threadKey = {thread}')
  except google.auth.exceptions.MutualTLSChannelError as e:
    logging.error(e)
    return e

  try:
    result = chat.spaces().messages().create(
      parent="/".join(thread.split("/")[:2]),
      body={'text': text, "thread": {"name": thread}}).execute()
  except Exception as e:
    logging.error(e)
    return e

  return result

if __name__ == '__main__':
  # Test from command line using:
  #   subnetcalc [args] - will only generate event of type MESSAGE
  ev = dict()
  ev['type'] = 'MESSAGE'
  ev['message'] = dict()
  ev['message']['text'] = '@Subnet Calculator ' + ' '.join(sys.argv[1:])
  print('Chat message sent: %s' % json.dumps(ev))
  response = do_subnetcalc(' '.join ( ev['message']['text'].split()[2:] ) )
  print('Response: %s' % response)