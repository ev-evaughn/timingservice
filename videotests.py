from colorama import init, Fore, Style
import socket as syssocket
import sys
import testCases
import time
import threading
import zmq

init()

def cPrint(s, color, **kwargs):
  print(f"{Style.NORMAL}{color}{s}{Style.RESET_ALL}", **kwargs)

def app(name: str, repport : str, reqport) -> None:
  reqThread = threading.Thread(target=request, args=(reqport,))
  repThread = threading.Thread(target=reply, args=(repport,))

  print(name + " running ...")
  reqThread.start()
  repThread.start()

  reqThread.join()
  repThread.join()

def request(port : str) -> None:
  ids = []

  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect(f'tcp://{syssocket.gethostname()}:{port}')

  cPrint(f'Clearing existing timers', Fore.BLUE, end='\n')
  try:
    socket.send_json({"from":"testing", "type":"get ids"})
    res = socket.recv_json()
    cPrint(str(res), Fore.GREEN)
    ids = res.get("payload").get("active ids") + \
          res.get("payload").get("history ids")
    print(ids)
    for id in ids:
      socket.send_json({"from":"testing", "type":"del", "payload":{"id":id}})
      res = socket.recv_json()
      if res.get("payload").get("status") == "OK":
        cPrint(f'deleted: {res.get("payload").get("id")}', Fore.GREEN)
      else:
        cPrint(f'failed to delete: {res.get("payload").get("id")}', Fore.RED)

  except Exception as e:
    cPrint(f"Deleting exception: {str(e)}", Fore.RED, end='\n\n')

  for test in testCases.baseCases:
    cPrint(f'Testing: {test}', Fore.BLUE)
    try:
      socket.send_json(test)
    except Exception as e:
      cPrint(f"Test request send error: {e}", Fore.RED)
      continue
    try:
      msg = socket.recv_json()
      if msg:
        payload = msg.get("payload")
        if payload:
          id = payload.get("id")
          status = payload.get("status")
          if id:
            ids.append(id)
          if status == "OK":
            cPrint(msg, Fore.GREEN)
          else:
            cPrint(msg, Fore.RED)
    except Exception as e:
      cPrint(f"Exception reading: {str(e)}", Fore.RED)

  try:
    socket.send_json({"from":"testing", "type":"cancel", "payload":{"id":ids[0]}})
    msg = socket.recv_json()
    if msg.get("payload").get("status") == "OK":
      cPrint(str(msg), Fore.GREEN)
    else:
      cPrint(str(msg), Fore.RED)
  except Exception as e:
    cPrint(f'Cancel error: {str(e)}', Fore.RED)

  try:
    socket.send_json({"from":"testing", "type":"del", "payload":{"id":ids[1]}})
    msg = socket.recv_json()
    if msg.get("payload").get("status") == "OK":
      cPrint(str(msg), Fore.GREEN)
    else:
      cPrint(str(msg), Fore.RED)
  except Exception as e:
    cPrint(f'Cancel error: {str(e)}', Fore.RED)
  
  print('\n\n\n')
  cPrint('Sending timers loop start', Fore.BLUE)
  for x in range(20):
    try:
      socket.send_json(
        {
          "from":"testing", 
          "type":"set timer", 
          "payload":{
                      "name":f"name of timer for {str(x)} seconds", 
                      "time":f"::{str(x)}",
                      "payload":[f"Any JSON for {str(x)}"]
          }
        }
      )
      msg = socket.recv_json()
      if msg.get("payload").get("status") == "OK":
        cPrint(str(msg), Fore.GREEN)
      else:
        cPrint(str(msg), Fore.RED)
    except Exception as e:
      cPrint(f'Timer loop error: {str(e)}', Fore.RED)
  cPrint('timer loop finished', Fore.BLUE)

def reply(port : str) -> None:
  try:
    context = zmq.Context()
    socket  = context.socket(zmq.REP)
    socket.bind("tcp://*:" + port)
  except Exception as e:
    cPrint(f"Test reply bind error: {str(e)}", Fore.RED)
  
  while True:
    msg = None
    try:
      msg = socket.recv_json()
    except Exception as e:
      cPrint(f'Test reply recv error: {str(e)}', Fore.RED)
      try:
        socket.send_json({"type":"error"})
      except Exception as e:
        cPrint(f'Test reply recv send error: {str(e)}', Fore.RED)

    if msg:
      id = msg.get("id")
      timerName = msg.get("name")
      if id and timerName:
        cPrint(f"id: {id}, name: {timerName}", Fore.GREEN)
        try:
          socket.send_json({"id":id})
        except Exception as e:
          cPrint(f'Test reply send error: {str(e)}', Fore.RED)

if __name__ == "__main__":
  args = sys.argv
  if len(args) != 3:
    print(f"Usage: python test.py REPPORT REQPORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1], sys.argv[2])

    except Exception as e:
      print("Exception raised trying to start program: ", e) 
