import grpc
import access_control_pb2
import access_control_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = access_control_pb2_grpc.AccessControlStub(channel)

uid = input("Entrez un UID à tester : ")
response = stub.CheckUID(access_control_pb2.UIDRequest(uid=uid))
print(f"Résultat : {response.message}")
