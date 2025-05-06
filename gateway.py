from flask import Flask, request
import grpc
import access_control_pb2
import access_control_pb2_grpc

app = Flask(__name__)

# Connection avec gRPC server
channel = grpc.insecure_channel('localhost:50051')
stub = access_control_pb2_grpc.AccessControlStub(channel)

@app.route('/uid', methods=['POST', 'OPTIONS'])
def receive_uid():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or 'uid' not in data:
        return "False", 400

    uid = data['uid']
    print(f"[GATEWAY] UID received: {uid}")


    try:
        grpc_request = access_control_pb2.UIDRequest(uid=uid)
        grpc_response = stub.CheckUID(grpc_request)

        access_granted = grpc_response.granted
    except Exception as e:
        print(f"[GATEWAY] Error contacting gRPC server: {e}")
        return "False", 500

    return str(access_granted), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)