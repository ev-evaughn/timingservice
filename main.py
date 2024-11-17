# The main program file for timingservice

from reply import wrapper
import subprocess
import sys

def app(name : str, port : str) -> None:  
  # start reply
  reply = None
  try:
    reply = subprocess.Popen(["python", "reply.py", "12345"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
  except Exception as e:
    print("Error starting reply: ", e)
    return

  # start alarm
  alarm = None
  try:
    alarm = subprocess.Popen(["python", "alarm.py"], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE
    )
  except Exception as e:
    print("Exception raised starting alarm.py: ", e)
    return

  print(name + " running ...")

  while True:
    pass

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