import socket
import threading
import time
import json
import ssl


# Fonction pour se connecter au serveur et vérifier l'authentification
def connect_to_server(server_ip, port, password, cert_pem):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cadata=cert_pem)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ssl_socket = context.wrap_socket(client_socket, server_hostname="example.com")
    ssl_socket.connect((server_ip, port))

    # Connexion au serveur avec le mot de passe
    ssl_socket.send(password.encode('utf-8'))

    print("Server password sent")

    # Vérifier si le mot de passe est correct
    response = ssl_socket.recv(1024).decode('utf-8')
    print(response)

    if "incorrect" in response:
        print("Mot de passe incorrect. Déconnexion...")
        ssl_socket.close()
        return None

    return ssl_socket


def close_connection(client_socket):
    client_socket.close()


# Fonction pour envoyer des commandes et recevoir les résultats
def send_commands(socket, command):
    # Envoyer la commande au serveur
    socket.send(command.encode('utf-8'))


def receive_data(server_socket):
    # Recevoir et afficher le résultat de la commande
    data = ""
    while True:
        try:
            chunk = server_socket.recv(1024).decode('utf-8')
            if chunk == "end":
                destination, data = data.split("|", 1)
                if destination == "metrics":
                    return server_socket.getpeername()[0], destination, json.loads(data)
                elif destination == "cmd":
                    return server_socket.getpeername()[0], destination, data
            data += chunk
        except Exception as e:
            break



def test(server):
    while True:
        servername, destination, data = receive_data(server)
        print(f'Serveur : {servername}, Destination : {destination} \n Donnée: \n {data}')


def run_client(server_ip, port, password):
    # Connexion au serveur pour les commandes
    server = connect_to_server(server_ip, port, password)

    if server:
        print("a")
        data = threading.Thread(target=test, args=(server,))
        data.start()
        a = 0
        while a < 10:
            send_commands(server, "show_metrics")
            send_commands(server, "ls")
            time.sleep(0.1)
            a += 1
        data.join()
        # Fermer la connexion après l'exécution de la commande
        server.close()


if __name__ == "__main__":
    server_ip = '192.168.1.9'  # Remplacer par l'IP du serveur
    port = 55555
    password = "a"  # Mot de passe pour l'authentification
    run_client(server_ip, port, password)
