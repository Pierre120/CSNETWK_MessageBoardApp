#########################################
# Message Board Project [Client-side]   #
# Group no: 15                          #
# Members:                              #
#     Cruz, Arion John                  #
#     Hernandez, Pierre Vincent         #
#########################################
import socket
import sys
import json

# Global variables 

# For storing the username of
# the client side's current user
curr_user = ''

# This dictionary will track the
# current status of the user
status = {
  "ready"      : False,
  "registered" : False,
  "sending"    : True
}

# Valid server addresses
valid_addr = ["172.16.0.20", "172.16.0.10"] # [CSNET01, CSNET02]

# String prompts for the return codes
ret_prompts = {
  "reg_401" : 'Registered successfully.',
  "reg_501" : 'Server unable to register the user. Please register your username again.',
    # vv This will return if the client is not registered inside the server.
  "501" : 'User not registered!\nPlease register again. Exiting...', 
  # vv This will return if the user is already exisiting in the curr_user
  "502" : 'User account already exists in chat room!\nUnsuccessful registration. Exiting..', 
  "dereg_401" : 'Disconnecting',
  "send_401" : 'Message sent successfully',
  "bad_req" : 'Bad request',
  "unk_retcode" : 'Unkown return code from server',
  "unk_response" : 'Unkown response received'
}

# This asks the client's preferred username for the registration
# process of the server and returns a dictionary object that
# consists of specified request command and username input.
def registration():
  global curr_user
  curr_user = input('Enter preferred username: ')
  register_req = {
    "command" : "register",
    "username" : curr_user
  }
  return register_req


# This function requires the client's username as its parameter
# in order to process the deregistration to the server
# by returning a dictionary object with specified command and username
def deregistration(user):
  deregister_req = {
    "command" : "deregister",
    "username" : user
  }
  return deregister_req


# This function is responsible for getting the text
# message from the user. It then forms the request
# dictionary and returns that dictionary
def send_message():
  global curr_user
  msg = input("Enter message: ")
  message_code = {
    "command" : "msg",
    "username" : curr_user,
    "message" : msg
  }
  return message_code


# This function handles the registration-related
# responses from the server side through knowing the meaning
# of the return_codes included in its "response" paramater.
# It returns the corresponding ret_codes-equivalent of the response,
# or flags the unk_response function if there's KeyError detected.
def process_registration(response):
  global ret_prompts
  try:
    if response["command"] == "ret_code":
      ret_codes = {
        201 : ret_prompts["bad_req"],
        301 : ret_prompts["bad_req"],
        401 : ret_prompts["reg_401"],
        501 : ret_prompts["reg_501"],
        502 : ret_prompts["502"],
      }
      return ret_codes.get(response["code_no"], ret_prompts["unk_retcode"])
  except KeyError:
    return ret_prompts["unk_response"]
  except TypeError:
    return ret_prompts["unk_response"]

# This function handles the deregistration-related
# responses from the server. It returns the corresponding
# ret_codes-equivalent of the response, or flags the
# unk_response function if there's KeyError detected.
def process_deregistration(response):
  global ret_prompts
  try:
    if response["command"] == "ret_code":
      ret_codes = {
        201 : ret_prompts["bad_req"],
        301 : ret_prompts["bad_req"],
        401 : ret_prompts["dereg_401"],
        501 : ret_prompts["501"]
      }
      return ret_codes.get(response["code_no"], ret_prompts["unk_retcode"])
  except KeyError:
    return ret_prompts["unk_response"]
  except TypeError:
    return ret_prompts["unk_response"]

# This function handles the message-related
# responses from the server. It returns the corresponding
# ret_codes-equivalent of the response, or flags the
# unk_response function if there's KeyError detected.
def process_sendmessage(response):
  global ret_prompts
  try:
    if response["command"] == "ret_code":
      ret_codes = {
        201 : ret_prompts["bad_req"],
        301 : ret_prompts["bad_req"],
        401 : ret_prompts["send_401"],
        501 : ret_prompts["501"]
      }
      return ret_codes.get(response["code_no"], ret_prompts["unk_retcode"])
  except KeyError:
    return ret_prompts["unk_response"]
  except TypeError:
    return ret_prompts["unk_response"]




# FOR CREATING A SOCKET WITH GIVEN ADDRESS AND PORT
while status["ready"] == False:
  try:
    # Set variables for server address and destination port
    server_host = input("Enter server IP Address: ")  # IP address of the server
    # Enter port number of server
    dest_port = int(input("Enter destination port number: "))
    # CREATE UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Program is ready for user registration
    if server_host in valid_addr: status["ready"] = True
  except ValueError:
    print('Entered port is not of a numerical value')
  except:
    print('Error from creating UDP socket!')


# FOR REGISTRATION PROCESS
while status["ready"] and status["registered"] == False:
  try:
    # User registration
    request = registration()
    # Parse registration request into JSON string
    request_json = json.dumps(request)
    # Send JSON string as bytes to the server
    sent = sock.sendto(bytes(request_json,"utf-8"), (server_host,dest_port))
    # Wait for response from server
    data, server = sock.recvfrom(1024)
    # Load JSON string response from server to Dictionary object
    response_dict = json.loads(data.decode("utf-8"))
    # Process the registration return code
    str_prompt = process_registration(response_dict)

    # Print prompt
    print(str_prompt)

    # Check for loop terminating conditions
    if str_prompt == ret_prompts["reg_401"]: status["registered"] = True
    elif str_prompt == ret_prompts["502"]: break # User account exists
  except json.decoder.JSONDecodeError: #catch error from json.loads()
    print('Problem loading JSON string!')
  except:
    print('Error from sending or receiving bytes!')


# FOR SENDING MESSAGE and DEREGISTRATION PROCESS
while status["registered"] and status["sending"]:
  # User enters message
  request = send_message()

  if request["message"] == "bye":
    status["sending"] = False
    # FOR DEREGISTRATION
    request = deregistration(curr_user)

  try:
    # Parse sending of message request into JSON string
    request_json = json.dumps(request)
    # Send JSON string as bytes to the server
    sent = sock.sendto(bytes(request_json,"utf-8"), (server_host,dest_port))
    # Wait for response from server
    data, server = sock.recvfrom(1024)
    # Load JSON string response from server to Dictionary object
    response_dict = json.loads(data.decode("utf-8"))

    # Check what type of process should be done
    if status["sending"] != True:
      # Process the deregistration return code
      str_prompt = process_deregistration(response_dict)

      # Check if deregistration is a success
      if str_prompt != ret_prompts["dereg_401"]: status["sending"] = True
    else:
      # Process the message return code
      str_prompt = process_sendmessage(response_dict)

    # Print prompt
    print(str_prompt)

    # User not registered
    # Possibly caused by the abrupt restart on the server side that results to 
    # clearing the list of users
    if response_dict["code_no"] == 501: break

  except json.decoder.JSONDecodeError: #catch error from json.loads()
    print('Problem loading JSON string!')
  except:
    print('Error from sending or receiving bytes!')


# CLOSE SOCKET
sock.close()

