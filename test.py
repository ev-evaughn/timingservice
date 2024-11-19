from colorama import init, Fore, Style
import socket as syssocket
import sys
import testCases
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

#  for test in testCases.interCases:
#    if len(ids) > 0:
#      string = test.format(ids.pop())
#      cPrint(f'Testing: {string}', Fore.BLUE)
#      try:
#        socket.send_string(string)
#      except Exception as e:
#        cPrint(f'Test req inter send error: {str(e)}', Fore.RED)
#        continue
#      try:
#        msg = socket.recv_json()
#        if msg:
#          cPrint(f'{str(msg)}', Fore.GREEN)
#      except Exception as e:
#        cPrint(f'Test req inter recv error: {str(e)}', Fore.RED)      
  if len(ids) > 1:
    first = {"from":"testing", "type":"cancel", "payload":{"id":ids.pop()}}
    second = {"from":"testing", "type":"del", "payload":{"id":ids.pop()}}

    cPrint(f'Testing: {str(first)}', Fore.BLUE)
    try:
      socket.send_json(first)
    except Exception as e:
      cPrint(f'Test req inter send error: {str(e)}', Fore.RED)
    try:
      msg = socket.recv_json()
      if msg:
        cPrint(str(msg), Fore.GREEN)
    except Exception as e:
      cPrint(f'Test req inter recv error: {str(e)}', Fore.RED)
    
    cPrint(f'Testing: {str(second)}', Fore.BLUE)
    try:
      socket.send_json(second)
    except Exception as e:
      cPrint(f'Test req inter send error: {str(e)}', Fore.RED)
    try:
      msg = socket.recv_json()
      if msg:
        cPrint(str(msg), Fore.GREEN)
    except Exception as e:
      cPrint(f'Test req inter recv error: {str(e)}', Fore.RED)

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
