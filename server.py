import grpc
from concurrent import futures
import access_control_pb2
import access_control_pb2_grpc
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Liste de UIDs autorisés
AUTHORIZED_UIDS = {"12345678", "ABCD1234", "DEADBEEF"}

@app.route('/uid', methods=['POST'])
def receive_uid():
    data = request.get_json()
    if not data or 'uid' not in data:
        return jsonify({"message": "UID missing"}), 400

    uid = data['uid']
    print(f"[INFO] UID reçu : {uid}")

    # Contact gRPC server to check if UID is authorized
    channel = grpc.insecure_channel('localhost:50051')
    stub = access_control_pb2_grpc.AccessControlStub(channel)
    grpc_request = access_control_pb2.UIDRequest(uid=uid)
    
    try:
        grpc_response = stub.CheckUID(grpc_request)
        return jsonify({"granted": grpc_response.granted, "message": grpc_response.message}), 200
    except Exception as e:
        return jsonify({"message": f"Error contacting gRPC server: {str(e)}"}), 500


class AccessControlServicer(access_control_pb2_grpc.AccessControlServicer):
    def CheckUID(self, request, context):
        uid = request.uid
        print(f"[INFO] UID reçu : {uid}")

        if uid in AUTHORIZED_UIDS:
            return access_control_pb2.AccessResponse(granted=True, message="Accès autorisé")
        else:
            return access_control_pb2.AccessResponse(granted=False, message="Accès refusé")


def run_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    access_control_pb2_grpc.add_AccessControlServicer_to_server(AccessControlServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()


if __name__ == '__main__':
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()

    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
