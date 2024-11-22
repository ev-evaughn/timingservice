import json
import select
import sys
import zmq

def alarm():
    try:
        alarms = []
        context = zmq.Context()
        socket = context.socket(zmq.REQ)

        alarm = None
        print('alarm running ...', file=sys.stderr)
        while True:
            try:
                rfds, _, _ = select.select([sys.stdin], [], [], 2)
                if rfds:
                        #print(f'alarm select rfds: {str(rfds)}, wfds: {str(wfds)}, alarm: {str(alarm)}', file=sys.stderr)
                        #if sys.stdin in rfds and not alarm:
                        #    alarm = json.loads(sys.stdin.readline())
                        #    print(f'connecting to {alarm.get("address")}', file=sys.stderr)
                        #    socket.connect(alarm.get("address"))
                        #    socket.send_json({"id":alarm.get("timerID"), "name":alarm.get("timerName"), "payload":alarm.get("payload")})
                        #if socket in rfds and alarm:
                        #    print(json.dumps(socket.recv_json()), file=sys.stdout)
                        #    sys.stdout.flush()
                        #    socket.disconnect(alarm.get("address"))
                        #    alarm = None
                    alarm = json.loads(sys.stdin.readline())
                    print(f'alarm alarm: {str(alarm)}', file=sys.stderr)
                    socket.connect(alarm.get("address"))
                    id = alarm.get("timerID")
                    secret = alarm.get("from")
                    socket.send_json({"id":id, "name":alarm.get("timerName"), "payload":alarm.get("payload")})
                    if socket.recv_json().get("id") == id:
                        print(json.dumps({"id":id, "from":secret}), file=sys.stdout)
                        sys.stdout.flush()
                    else:
                        print('ack failed', file=sys.stderr)
                else:
                    print('alarm nothing read', file=sys.stderr)

            except Exception as e:
                print(f'alarm: {str(e)}', file=sys.stderr)
    except Exception as e:
        print(f'alarm exception: {str(e)}', file=sys.stderr)

if __name__ == "__main__":
    alarm()
