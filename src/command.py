import dotenv
import json
import os
import sys
import zmq

dotenv.load_dotenv(dotenv.find_dotenv())

def command():
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(os.environ.get("BINDADDR"))

        print('command running ...', file=sys.stderr)
        while True:
            try:
                inMsg = socket.recv_json()
                #print(f'command inMsg: {str(inMsg)}', file=sys.stderr)
            except Exception as e:
                try:
                    socket.send_json(
                        {
                            "type":"error",
                            "payload":{
                                "status":"FAILED",
                                "msg":f"ZMQ recv_json exception: {str(e)}"
                            }
                        }
                    )
                    continue
                except Exception as e:
                    print(f'command exception: {str(e)}', file=sys.stderr)

            print(json.dumps(inMsg), file=sys.stdout)
            sys.stdout.flush()

            try:
                socket.send_json(json.loads(sys.stdin.readline()))
            except Exception as e:
                print(f'command exception: {str(e)}', file=sys.stderr)
    except Exception as e:
        print(f'command exception: {st(e)}', file=sys.stderr)

if __name__ == "__main__":
    command()
