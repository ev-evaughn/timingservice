# The main program file for timingservice

import db
import subprocess
import sys
import zmq

def app(name : str, port : str) -> None:
  try:
    repContext = zmq.Context()
    repSocket  = repContext.socket(zmq.REP)
    repSocket.bind("tcp://*:" + port)

  except Exception as e:
    print("Exception raised setting up zmq REP socket: ", e)
    return
  
  try:
    alarmProc = subprocess.Popen(
        ["python", "alarm.py"], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE
    )

  except Exception as e:
    print("Exception raised starting alarm.py: ", e)
    return

  print(name + " running ...")
  while True:
    pass

def wrapper(request : object) -> object:
  requestType = request.get("type")
  if requestType == "echo":
    return request
  
  elif requestType == "set address":
    return {}
  
  elif requestType == "set timezone":
    return {}
  
  #elif requestType == 

if __name__ == "__main__":
  args = sys.argv
  if len(args) != 2:
    print(f"Usage: python main.py PORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1])
    
    except Exception as e:
      print("Exception raised trying to start program: ", e)