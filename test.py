from colorama import init, Fore, Style
import socket
import sys
import zmq

def cPrint(s, color, **kwargs):
  print(f"{Style.NORMAL}{color}{s}{Style.RESET_ALL}", **kwargs)

def app(name: str, repport : str, reqport) -> None:
  testCases = [
    {
      "from":"testing",
      "type":"set address",
      "payload":{
        "address":f'tcp://{socket.gethostname()}:{repport}'
      }
    },
    {
      "from":"testing",
      "type":"set timezone",
      "payload":{
        "timezone":-8
      }
    },
    {
      "from":"testing",
      "type":"set timer",
      "payload":{
        "name":"timer one",
        "time":"::2",
        "payload":{"test":0}
      }
    }
]
  
  try:
    repContext = zmq.Context()
    repSocket  = repContext.socket(zmq.REP)
    repSocket.bind("tcp://*:" + repport)

  except Exception as e:
    print("Exception raised setting up zmq REP socket: ", e)
    return
  
  print(name + " running ...")

  reqContext = zmq.Context()
  reqSocket = reqContext.socket(zmq.REQ)
  reqSocket.connect(f'tcp://{socket.gethostname()}:{reqport}')
  for test in testCases:
    cPrint(f'Testing: {test}', Fore.BLUE)
    reqSocket.send_json(test)
    try:
      cPrint(reqSocket.recv_json(), Fore.GREEN)

    except Exception as e:
      cPrint(f"Exception reading: {str(e)}", Fore.RED)

if __name__ == "__main__":
  args = sys.argv
  if len(args) != 3:
    print(f"Usage: python test.py REPPORT REQPORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1], sys.argv[2])

    except Exception as e:
      print("Exception raised trying to start program: ", e) 