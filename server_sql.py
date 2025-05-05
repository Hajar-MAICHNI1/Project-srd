import grpc
from concurrent import futures
import access_control_pb2
import access_control_pb2_grpc
import pyodbc

# Configuration de la connexion SQL Server
SERVER = 'localhost' 
DATABASE = 'RFIDAccessDB'
USERNAME = 'sa'
PASSWORD = 'azerty'
DRIVER = '{ODBC Driver 17 for SQL Server}' 

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

# Implémentation du service gRPC
class AccessControlServicer(access_control_pb2_grpc.AccessControlServicer):
    def CheckUID(self, request, context):
        uid = request.uid
        print(f"[INFO] Reçu UID: {uid}")

        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()

                # Journaliser la tentative
                cursor.execute("INSERT INTO AccessLogs (uid) VALUES (?)", (uid,))
                conn.commit()

                # Vérifier si le UID est autorisé
                cursor.execute("SELECT uid FROM AuthorizedCards WHERE uid = ?", (uid,))
                result = cursor.fetchone()

                if result:
                    return access_control_pb2.AccessResponse(granted=True, message="Accès autorisé")
                else:
                    return access_control_pb2.AccessResponse(granted=False, message="Accès refusé")

        except Exception as e:
            print(f"[ERREUR] {e}")
            return access_control_pb2.AccessResponse(granted=False, message="Erreur serveur")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    access_control_pb2_grpc.add_AccessControlServicer_to_server(AccessControlServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Serveur gRPC en écoute sur le port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
