import datetime
import db
import sys
import zmq

def app() -> None:
  # Get the alarms for the next 10 min
  pass

# Start program
if __name__ == "__main__":
  args = sys.argv
  if len(args) != 1:
    print("Usage: python alarm.py", file=sys.stderr)
  
  else:
    try:
      app()

    except Exception as e:
      print(f"Exception starting alarm: {str(e)}", file=sys.stderr)