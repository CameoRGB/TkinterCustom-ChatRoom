import socket
import threading
import random
import data as Q

HOST = '127.0.0.1' 
PORT = 1234

BOLD = "\033[1m"
RESET = "\033[0m"

clients = []
nicknames = []

def get_random_leave_quote():
    return random.choice(Q.quotes_leave)

def broadcast(message):
    clients_copy = clients[:] 
    
    for client in clients_copy:
        try:
            client.send(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message:
                broadcast(message)
            else:
                raise Exception("Client disconnected")

        except Exception as e:
            if client in clients:
                index = clients.index(client)
                
                clients.remove(client)
                client.close()
                
                if index < len(nicknames):
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                else:
                    nickname = "Anonym"

                leave_quote = get_random_leave_quote() 
                broadcast(f'{nickname} {leave_quote}'.encode('utf-8'))
                
                print(f'{nickname} left the chat. Reason: {e}')
            break


def receive():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server runs on {BOLD}{HOST}:{PORT}{RESET}")

    while True:
        client, address = server.accept()
        print(f"New connection: {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        
        nicknames.append(nickname)
        clients.append(client)

        print(f"Clients name is {BOLD}{nickname}{RESET}")
        client.send('Connected to server'.encode('utf-8'))
        
        join_quote = random.choice(Q.quotes_join)
        broadcast(f"{nickname} {join_quote}.".encode('utf-8'))
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()