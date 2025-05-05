import grpc
from concurrent import futures
import access_control_pb2
import access_control_pb2_grpc

# liste de UIDs autorisés
AUTHORIZED_UIDS = {"12345678", "ABCD1234", "DEADBEEF"}

class AccessControlServicer(access_control_pb2_grpc.AccessControlServicer):
    def CheckUID(self, request, context):
        uid = request.uid
        print(f"[INFO] UID reçu : {uid}")

        if uid in AUTHORIZED_UIDS:
            return access_control_pb2.AccessResponse(granted=True, message="Accès autorisé")
        else:
            return access_control_pb2.AccessResponse(granted=False, message="Accès refusé")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    access_control_pb2_grpc.add_AccessControlServicer_to_server(AccessControlServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Serveur lancé sur le port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
