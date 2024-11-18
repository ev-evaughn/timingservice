# The main program file for timingservice

import select
import subprocess
import sys

def app(name : str, port : str) -> None:  
  # start reply
  reply = None
  try:
    reply = subprocess.Popen(["python", "reply.py", "12345"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
  except Exception as e:
    print("Error starting reply: ", e)
    return
  
  # start alarm
  alarm = None
  try:
    alarm = subprocess.Popen(["python", "alarm.py"], 
        stdin=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
  except Exception as e:
    print("Exception raised starting alarm.py: ", e)
    return

  # main program
  print(name + " running ...")
  while True:
    rlist, wlist, _ = select.select([reply.stderr, alarm.stderr, reply.stdout], [alarm.stdin], [])
    for fd in rlist:
      if fd.fileno() == reply.stdout.fileno() and wlist:
        msg = fd.readline()
        if msg:
            print(msg, file=alarm.stdin, end='')
            print('main wrote to alarms stdin')
      else:
        msg = fd.readline()
        if msg:
            print(msg, end='')

# Start program
if __name__ == "__main__":
  args = sys.argv
  if len(args) != 2:
    print(f"Usage: python main.py PORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1])
    
    except Exception as e:
      print("Exception raised trying to start program: ", e)
