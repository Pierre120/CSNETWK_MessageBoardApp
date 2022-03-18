#########################################
# Message Board Project [Server-side]   #
# Group no: 15                          #
# Members:                              #
#     Cruz, Arion John                  #
#     Hernandez, Pierre Vincent         #
#########################################

import socket
import sys
import json


# Create an empty list to store the
# usernames of currently logged in users.
curr_users = []

# Set variables for listening address and listening port
listening_addr = "172.16.0.20"
# CSNET01 - 172.16.0.20
# CSNET02 - 172.16.0.10
listening_port = 8015

# Define and temporarily initialize response/return code
response = {
  "command": "ret_code",
  "code_no": 000
}

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



# This function is responsible for returning
# the return code value specified by the given key.
def ret_code(key):
  # Return codes Dictionary
  return_codes = {
    "incomplete": 201, # Command parameters incomplete
    "unknown": 301, # Command unknown
    "accepted": 401, # Command accepted
    "not_reg": 501, # User not registered
    "usr_exist": 502 # User account exists
  }
  return return_codes[key]

# This function is responsible for registering the user
def reg_user(req):
  global curr_users
  try:
    #Checks if user already exists
    if req["username"] in curr_users: return ret_code("usr_exist")

    # Registers the user if it doesn't exist
    curr_users.append(req["username"])
    # Print currently logged in users
    print("Users in message board: %s" %curr_users)
    return ret_code("accepted")
  except KeyError:
    return ret_code("incomplete")
  except: # Failed to register user
    return ret_code("not_reg")


# This function is responsible for deregistering the user
def dereg_user(req):
  global curr_users
  try:
    # Check if requesting user is registered before
    # proceeding in deregistration
    if req["username"] not in curr_users: return ret_code("not_reg")

    print("User %s exiting..." %req["username"])
    # Deregisters the user
    curr_users.remove(req["username"])
    # Print remaining users
    print("Users in message board: %s" %curr_users)
    return ret_code("accepted")
  except KeyError:
    return ret_code("incomplete")


# This function is responsible for posting the message
def send_msg(req):
  try:
    # Check if requesting user is registered before
    # proceeding in sending message
    if req["username"] not in curr_users: return ret_code("not_reg")

    # Prints out the message
    print("from %s : %s" %(req["username"], req["message"]))
    return ret_code("accepted")
  except KeyError:
    return ret_code("incomplete")


# Function for processing request commands.
# It calls the other functions responsible
# for a specific command
def process_req(req):
  global return_codes
  # Switch case for commands
  commands = {
    "register": reg_user,
    "deregister": dereg_user,
    "msg": send_msg
  }
  try:
    # Get the command that needs to be executed
    res = commands.get(req["command"], ret_code("unknown"))
    # Execute command and return the response
    return res(req)
  except KeyError:
    return ret_code("incomplete")
  except TypeError:
    return ret_code("unknown")



# Bind the socket
sock.bind((listening_addr,listening_port))

# START LISTENING FOR REQUESTS
print("starting up on graphitex port %d" %listening_port)
print("\nwaiting to receive message")
while True:

  # Waiting for data to arrive, this is a blocking function
  data,address = sock.recvfrom(1024)

  # Checks if received data contains something
  if data:
    try:
      # Load the JSON string request from
      # connecting client to a Dictionary object
      request = json.loads(data.decode("utf-8")) # may raise an error

      # Process the request from connecting client
      response["code_no"] = process_req(request)

      # Convert response to JSON string
      res_json = json.dumps(response)

      # Send return code to connecting client
      sent = sock.sendto(bytes(res_json,"utf-8"), address)
    except: # catch all errors that may occur
      continue

