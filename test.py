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
      "type":"get address",
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
      "type":"get timezone"
    },
    {
      "type":"echo"
    },
    {
      "from":"testing",
      "type":"set timer",
      "payload":{
        "name":"timer one",
        "time":"::2",
        "payload":{"test":0}
      }
    },
    {
      "from":"testing",
      "type":"set alarm",
      "payload":{
        "name":"timer two",
        "datetime":"2024-12-25 05:00:00",
        "payload":{"msg":"merry xmas"}
      }
    },
    {
      "from":"testing",
      "type":"cancel",
      "payload":{
        "id":1
      }
    },
    {
      "from":"testing",
      "type":"del",
      "payload":{
        "id":1
      }
    },
    {
      "from":"testing",
      "type":"get",
      "payload":{
        "id":17
      }
    },
    {
      "from":"testing",
      "type":"get ids"
    },
    {
      "from":"testing",
      "type":"get active",
    },
    {
      "from":"testing",
      "type":"get active",
      "payload":{
        "limit":1,
        "start":1
      }
    },
    {
      "from":"testing",
      "type":"get history",
      "payload":{}
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

  cPrint(f'Clearing existing timers', Fore.BLUE, end='\n')
  try:
    reqSocket.send_json({"from":"testing", "type":"get ids"})
    res = reqSocket.recv_json()
    cPrint(str(res), Fore.GREEN)
    ids = res.get("payload").get("active ids") + \
          res.get("payload").get("history ids")
    print(ids)
    for id in ids:
      reqSocket.send_json({"from":"testing", "type":"del", "payload":{"id":id}})
      res = reqSocket.recv_json()
      if res.get("payload").get("status") == "OK":
        cPrint(f'deleted: {res.get("payload").get("id")}', Fore.GREEN)
      else:
        cPrint(f'failed to delete: {res.get("payload").get("id")}', Fore.RED)

  except Exception as e:
    cPrint(f"Deleting exception: {str(e)}", Fore.RED, end='\n\n')

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