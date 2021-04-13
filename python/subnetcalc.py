
from flask import request, json
import ipaddress, sys

usage = """

*Usage:*

  @Subnet Calculator range <aa.bb.cc.dd/mm> - _show range of IPs represented by Subnet_

"""

def on_event(request):
  """Handles an event from Google Chat."""
  event = request.get_json()
  if event['type'] == 'ADDED_TO_SPACE':
    resp = 'Thanks for adding me to "%s"!\n' % (event['space']['displayName'] if event['space']['displayName'] else 'this chat')
    resp += usage
  elif event['type'] == 'MESSAGE':
    resp = do_subnetcalc(' '.join ( event['message']['text'].split()[2:] ) )
  else:
    return
  return json.jsonify({'text': resp})

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

  return "*" + cidr_text + ":* " + \
    str(cidr_block[0]) + " - " + str(cidr_block[cidr_block.num_addresses - 1]) + \
    " (Usable addresses: " + str(cidr_block[1]) + " - " + str(cidr_block[cidr_block.num_addresses - 2]) + ")"


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