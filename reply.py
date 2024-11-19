import datetime
import db
from dotenv import load_dotenv, find_dotenv
import os
import json
import re
import sys
import zmq

load_dotenv(find_dotenv())
UTC = datetime.timezone(datetime.timedelta(hours=int(os.environ.get("UTC"))))
strTimeF = '%Y-%m-%d %H:%M:%S.%f'

def app(name : str, port : str) -> None:
  # Bind REP context socket
  try:
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + port)

  except Exception as e:
    raise Exception(f"reply setting up zmq REP socket: {str(e)}")

  # Main program loop
  while True:
    try:
      # Receive Request
      inMsg = None
      try:
        inMsg = socket.recv_json()
  
      except Exception as e:
        socket.send_json({
          "type":"error",
          "payload":{
            "status":"FAILED",
            "msg":f"ZMQ receive error: {str(e)}"
          }
        })
        continue
  
      # Process Request
      outMsg = None
      try:
        outMsg = wrapper(inMsg)
  
      except Exception as e:
        socket.send_json({
          "type":"error",
          "payload":{
            "status":"FAILED",
            "msg":f"Failed to process request: {str(e)}"
          }
        })
        continue
  
      # Send reply
      try:
        socket.send_json(outMsg)
  
      except Exception as e:
        print("Exception raised sending: ", e, file=sys.stderr)
    except Exception as e:
      print(f"Main program loop exception: {str(e)}", file=sys.stderr)
      context = zmq.Context()
      socket = context.socket(zmq.REP)
      socket.bind("tcp://*:" + port)


def wrapper(request : object) -> object:
  requestType = request.get("type")
  if requestType == "echo":
    return request
  
  elif requestType == "set address":
    try:
      return setAddress(request)
    except Exception as e:
      return failed("set address", str(e))
    
  elif requestType == "get address":
    try:
      return getAddress(request)
    except Exception as e:
      return failed("get address", str(e))
  
  elif requestType == "set timezone":
    try:
      return setTimezone(request)
    except Exception as e:
      return failed("set timezone", str(e))
    
  elif requestType == "get timezone":
    try:
      return getTimezone(request)
    except Exception as e:
      return failed("get timezone", str(e))
  
  elif requestType == "set timer":
    try:
      return setTimer(request)
    except Exception as e:
      return failed("set timer", str(e))

  elif requestType == "set alarm":
    try:
      return setAlarm(request)
    except Exception as e:
      return failed("set alarm", str(e))

  elif requestType == "cancel":
    try:
      return cancel(request)
    except Exception as e:
      return failed("cancel", str(e))

  elif requestType == "del":
    try:
      return delete(request)
    except Exception as e:
      return failed("del", str(e))

  elif requestType == "get":
    try:
      return get(request)
    except Exception as e:
      return failed("get", str(e))

  elif requestType == "get ids":
    try:
      return getIds(request)
    except Exception as e:
      return failed("get ids", str(e))

  elif requestType == "get active":
    try:
      return getActive(request)
    except Exception as e:
      return failed("get active", str(e))

  elif requestType == "get history":
    try:
      return getHistory(request)
    except Exception as e:
      return failed("get history", str(e))
    
  else:
    return failed(requestType, "Request \"type\" not recognized.")
  
def failed(type : str, error : str) -> object:
  return {"type":type, "payload":{"status":"FAILED", "msg":error}}

def success(type: str) -> object:
  return {"type":type, "payload":{"status":"OK", "msg":None}}
    
def soon(id : int, name : str = '', time : datetime.datetime = None, payload : object = None, address : str = '', ack : bool = False) -> None:
  try:
    try:
      if ack:
        try:
          print(json.dumps({"timerID":id, "ack":True}))
          sys.stdout.flush()
        except Exception as e:
          print(f'Reply soon ack error: {str(e)}', file=sys.stderr)
      elif name and payload and address and time:
        now = datetime.datetime.now()
        tenmin = now + datetime.timedelta(minutes=10)
        #print(f'tenmin: {str(type(tenmin))} time: {str(type(time))}', file=sys.stderr)

        if (time < tenmin):
          try:
            timeStr = time.strftime(strTimeF)
            print(json.dumps({"timerID":id, "timerName":name, "time":timeStr, "payload":payload, "address":address}))
            sys.stdout.flush()
          except Exception as e:
            print(f'Reply soon time to str error: {str(e)}', file=sys.stderr)
        else:
          print(f'another sanity check', file=sys.stderr)
      else:
        raise Exception(f'missing parameter: name={name}, time={str(time)}, payload={str(payload)}, address={address}') 
    except Exception as e:
      print(f'Reply soon sanity check: {str(e)}', file=sys.stderr)
  except Exception as e:
    print(f"Reply soon exception: {str(e)}", file=sys.stderr)
  

def getAddress(req : object) -> object:
  secret = req.get("from")
  if secret:
    sql = f'SELECT address FROM timingserviceUsers WHERE ' + \
          f'secret = "{secret}";'
    try:
      res = db.query(sql)
      if res:
        return  {
                  "type":"get address",
                  "payload":{
                    "status":"OK",
                    "msg":None,
                    "address":res[0]
                  }
                }
      else:
        raise Exception("DB did not return address.")
    except Exception as e:
      raise Exception(f"DB error: {str(e)}")
  else:
    raise Exception('"secret" missing.')

def setAddress(req : object) -> object:
  payload = req.get("payload")
  secret = req.get("from")
  if payload and secret:
    address = payload.get("address")
    if address:
      sql = f'UPDATE timingserviceUsers SET address = "{address}" WHERE ' + \
            f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}");'
      res = db.query(sql)
      
      if not res:
        return  {
                  "type":"set address",
                  "payload":{
                    "status":"OK",
                    "msg":None
                  }
                }
      else:
        raise Exception(f"DB error: {str(res)}.")
    else:
      raise Exception(f"Address missing.")
  else:
    raise Exception(f"Either payload or secret missing.")
  
def getTimezone(req : object) -> object:
  secret = req.get("from")
  if secret:
    sql = f'SELECT timezone FROM timingserviceUsers WHERE secret = "{secret}";'
    try:
      res = db.query(sql)
      if res:
        return  {
                  "type":"get timezone",
                  "payload":{
                    "status":"OK",
                    "msg":None,
                    "timezone":res[0]
                  }
                }
      else:
        raise Exception("DB did not return address.")
    except Exception as e:
      raise Exception(f"DB error: {str(e)}")
  else:
    raise Exception('"secret" missing.')

def setTimezone(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    timezone = payload.get("timezone")
    if timezone:
      sql = f'UPDATE timingserviceUsers SET timezone = {timezone} WHERE ' + \
            f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}");'
      res = db.query(sql)

      if not res:
        return  {
                  "type":"set timezone",
                  "payload":{
                    "status":"OK",
                    "msg":None
                  }
                }
      else:
        raise Exception(f'DB error: {str(res)}.')
      
    else:
      raise Exception(f'"timezone" missing.')
    
  else:
    raise Exception(f'"secret" or "payload" missing.')

def setTimer(req : object) -> object:
  global UTC

  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    name = payload.get("name")
    time = payload.get("time")
    payload = payload.get("payload")
    if name and time and payload:
      match = re.search(
          "^(?P<hour>\d{1,2})?:" + \
          "(?P<min>\d{1,2})?:" + \
          "(?P<sec>\d{1,2})?$", time)
      if match:
        matches = match.groupdict()
        hour = matches.get("hour") if matches.get("hour") else "0"
        min = matches.get("min") if matches.get("min") else "0"
        sec = matches.get("sec") if matches.get("sec") else "0"
        time = datetime.timedelta(
          seconds=int(sec),
          minutes=int(min),
          hours=int(hour)
        )
        time = time + datetime.datetime.now()#UTC) 
        sql = f'INSERT INTO timingserviceTimers (userID, timerName, time, payload) ' + \
              f'VALUES ((SELECT userID FROM timingserviceUsers WHERE secret = "{secret}"), ' + \
                        f'''"{name}", "{time.strftime(strTimeF)}", '{json.dumps(payload)}');'''
        
        sql2 =  f'SELECT timerID, address FROM timingserviceTimers JOIN ' + \
                f'timingserviceUsers ON timingserviceTimers.userID = ' + \
                f'timingserviceUsers.userID WHERE ' + \
                f'timingserviceTimers.userID = (SELECT userID FROM timingserviceUsers ' + \
                f'WHERE secret = "{secret}") and timerName = "{name}";'

        try:
          res = db.query(sql)
          if not res:
            res = db.query(sql2)
            if res:
              soon(res[0].get("timerID"), 
                   name, 
                   time, 
                   payload, 
                   res[0].get("address")
              ) 
              return  {
                        "type":"set timer",
                        "payload":{
                          "status":"OK",
                          "msg":None,
                          "id":res[0].get("timerID")
                        }
                      }
            else:
              raise Exception("Failed to retrieve id from DB.")
          else:
            raise Exception(f"DB error: {str(res)}")
        
        except Exception as e:
          raise Exception(f"DB query error: {str(e)}")
      else:
        raise Exception(f'regex match failed on "time".')
    else:
      raise Exception(f'"name" or "time" or "payload" missing.')
  else:
    raise Exception(f'"secret" or "payload" missing.')

def setAlarm(req : object) -> object:
  global UTC

  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    name = payload.get("name")
    time = payload.get("datetime")
    payload = payload.get("payload")
    if name and time and payload:
      sql = f'INSERT INTO timingserviceTimers ' + \
            f'(userID, timerName, time, payload) VALUES (' + \
            f'(SELECT userID FROM timingserviceUsers WHERE ' + \
                f'secret = "{secret}"), ' + \
            f'"{name}", "{time}", \'{json.dumps(payload)}\');'
      sql2 =  f'SELECT timerID, address FROM timingserviceTimers JOIN timingserviceUsers ON timingserviceTimers.userID = timingserviceUsers.userID WHERE ' + \
              f'timingserviceTimers.userID = (SELECT userID FROM timingserviceUsers ' + \
              f'WHERE secret = "{secret}") AND timerName = "{name}";'
      
      try:
        res = db.query(sql)
        if not res:
          try:
            res = db.query(sql2)
            if res:
              try:
                parsedTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
              except Exception as e:
                raise Exception(f'Reply setAlarm time parse error: {str(e)}')
              soon(res[0], name, parsedTime, payload, res[0].get("address")) 
              return  {
                        "type":"set alarm",
                        "payload":{
                          "status":"OK",
                          "msg":None,
                          "id":res[0].get("timerID")
                        }
                      }
            else:
              raise Exception("Failed to retrieve id from DB.")
          except Exception as e:
            raise Exception(f"Reply setAlarm DB error: {str(e)}, query: {sql2}")
        else:
          raise Exception(f"DB error: {str(res)}")
      except Exception as e:
        raise Exception(f"DB query error: {str(e)}, query: {sql}")
    else:
      raise Exception(f'"name" or "time" or "payload" missing.')
  else:
    raise Exception(f'"secret" or "payload" missing.')

def cancel(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    id = payload.get("id")
    if id:
      sql = f'UPDATE timingserviceTimers SET ack = "{datetime.datetime.now()}" WHERE timerID = {id} AND userID = (SELECT userID FROM timingserviceUsers WHERE secret = "{secret}");'
      try:
        res = db.query(sql)
        if not res:
          return  {
                    "type":"cancel",
                    "payload":{
                      "status":"OK",
                      "msg":None,
                      "id":id
                    }
                  }
        else:
          raise Exception(f"DB error: {str(res)}")
      except Exception as e:
        raise Exception(f'DB error: {str(e)}')
    else:
      raise Exception('"id" missing.')
  else:
    raise Exception('"secret" or "payload" missing.')

def delete(req: object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    id = payload.get("id")
    if id:
      sql = f'DELETE FROM timingserviceTimers WHERE timerID = {id} AND ' + \
            f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}");'
      try:
        res = db.query(sql)
        if not res:
          return  {
                    "type":"del",
                    "payload":{
                      "status":"OK",
                      "msg":None,
                      "id":id
                    }
                  }
        else:
          raise Exception(f"DB error: {str(res)}")
      except Exception as e:
        raise Exception(f"DB error: {str(e)}")
    else:
      raise Exception(f'"id" missing.')
  else:
    raise Exception(f'"secret" or "payload" missing.')

def get(req: object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    id = payload.get("id")
    if id:
      sql = f'SELECT timerID, timerName, time, payload, ack FROM timingserviceTimers WHERE userID = (SELECT userID FROM timingserviceUsers WHERE secret = "{secret}") AND timerID = {id};'

      try:
        res = db.query(sql)
        if res:
          timer = {
            "id":res[0].get("timerID"),
            "datetime":str(res[0].get("time")),
            "payload":res[0].get("payload"),
            "ack":res[0].get("ack")
          }
          return  {
                    "type":"get",
                    "payload":{
                      "status":"OK",
                      "msg":None,
                      "timer":timer
                    }
                  }
        else:
          raise Exception("DB did not return timer.")
      except Exception as e:
        raise Exception(f"DB error: {str(e)}")
    else:
      raise Exception('"id" missing.')
  else:
    raise Exception('"secret" or "payload" missing.')

def getIds(req : object) -> object:
  secret = req.get("from")
  if secret:
    time = datetime.datetime.now()
    sql = f'SELECT timerID FROM timingserviceTimers WHERE userID = ' + \
          f'(SELECT userID FROM timingserviceUsers WHERE ' + \
          f'secret = "{secret}") AND time > "{time}" AND ack IS null;'
    sql2 =  f'SELECT timerID FROM timingserviceTimers WHERE userID = ' + \
            f'(SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}") AND time <= "{time}" OR ack IS NOT null;'

    try:
      res = db.query(sql)
      active = []
      for id in res:
        active.append(id)

      res = db.query(sql2)
      history = []
      for id in res:
        history.append(id)

      return  {
                "type":"get ids",
                "payload":{
                  "status":"OK",
                  "msg":None,
                  "active ids":[x.get("timerID") for x in active],
                  "history ids":[x.get("timerID") for x in history]
                }
              }
    except Exception as e:
      raise Exception(f"DB error: {str(e)}")
  else:
    raise Exception('"secret missing.')

def getActive(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret:
    limit = None
    start = None
    if payload:
      limit = payload.get("limit")
      start = payload.get("start")

    sql = f'SELECT timerID, time, payload FROM timingserviceTimers WHERE ' + \
          f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
          f'secret = "{secret}") AND time > ' + \
          f'"{str(datetime.datetime.now())}" ' + \
          f'AND ack IS null ORDER BY time ASC' + \
          f'{f" LIMIT {limit}" if limit else ""}' + \
          f'{f" OFFSET {start}" if start else ""};'

    try:
      res = db.query(sql)
      if res:
        actives = []
        for x in res:
          actives.append({"id":x.get("timerID"), "datetime":str(x.get("time")), "payload":x.get("payload")})

        return  {
                  "type":"get active",
                  "payload":{
                    "status":"OK",
                    "msg":None,
                    "actives":actives
                  }
                }
      else:
        raise Exception("DB didn't return actives")
    except Exception as e:
      raise Exception(f"DB error: {str(e)}")
  else:
    raise Exception('"secret" missing.')

def getHistory(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret:
    limit = None
    start = None
    if payload:
      limit = payload.get("limit")
      start = payload.get("start")
    
    limit = f' LIMIT {limit}' if limit else ''
    start = f' OFFSET {start}' if start else ''

    sql = f'SELECT timerID, time, payload, ack FROM timingserviceTimers ' + \
          f'WHERE userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
          f'secret = "{secret}") AND time <= ' + \
          f'"{str(datetime.datetime.now())}"' + \
          f' OR ack IS NOT null ORDER BY time DESC{limit}{start};'

    try:
      res = db.query(sql)
      if res:
        histories = []
        for x in res:
          histories.append({"id":x.get("timerID"), "datetime":str(x.get("time")), "payload":x.get("payload"), "ack":x.get("ack")})

        return  {
                  "type":"get history",
                  "payload":{
                    "status":"OK",
                    "msg":None,
                    "histories":histories
                  }
                }
      else:
        raise Exception("DB did not return histories.")
    except Exception as e:
      raise Exception(f"DB error: {str(e)}")
  else:
    raise Exception('"secret" missing.')
  
# Start Program
if __name__ == "__main__":
  args = sys.argv
  if len(args) != 2:
    raise Exception('Usage: python reply.py PORT')

  else:
    try:
      app(sys.argv[0], sys.argv[1])

    except Exception as e:
      raise Exception("Trying to start reply program: ", e)
