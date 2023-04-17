# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/11_network.ipynb.

# %% auto 0
__all__ = ['Server', 'Client', 'ConnectionManager']

# %% ../nbs/11_network.ipynb 2
import socket
import json

# %% ../nbs/11_network.ipynb 3
class Server():
    def __init__(self, host='localhost', port=6666 , buf_size=1024):
        self.buf_size = buf_size
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print(f"Waiting for connection on {host}:{port}")
            self.connection, addr = s.accept()
            print(f"Connected by {addr}")
        self.open=True
            
    def get(self):
        data = self.connection.recv(self.buf_size)
        return data.decode()
    
    def put(self, data):
        d = str.encode(data)
        self.connection.sendall(d)

    def get_dict(self):
        data = self.connection.recv(self.buf_size)
        dict = eval(data.decode())
        #print('recv',dict)
        return dict
    
    def put_dict(self, dict):
        json_object = json.dumps(dict, indent = 4) 
        #print('send',json_object)       
        d = str.encode(json_object)
        self.connection.sendall(d)

    def isOpen(self):
        return self.open

    def finish(self):
        self.open = False

    def close(self):
        self.open=False
        self.connection.close()
        print('Closed server connection')

# %% ../nbs/11_network.ipynb 4
class Client():
    
    def __init__(self, host='localhost', port=6666 , buf_size=1024):
        self.buf_size = buf_size
        self.connection = socket.create_connection((host,port))
        self.open=True
    
    def get(self):
        data = self.connection.recv(self.buf_size)
        #print('recv',data)
        return data.decode()
    
    def put(self, data):
        d = str.encode(data)
        #print('send',data)       
        self.connection.sendall(d)

    def get_dict(self):
        data = self.connection.recv(self.buf_size)
        dict = eval(data.decode())
        return dict
    
    def put_dict(self, dict):
        json_object = json.dumps(dict, indent = 4) 
        d = str.encode(json_object)
        self.connection.sendall(d)

    def isOpen(self):
        return self.open

    def finish(self):
        self.open = False
        
    def close(self):
        self.connection.close()
        self.finish()
        #print('Closed client connection')


# %% ../nbs/11_network.ipynb 5
class ConnectionManager:
    "A utility for managing a client socket connection."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if ConnectionManager.__instance == None:
             ConnectionManager()
        return ConnectionManager.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if ConnectionManager.__instance != None:
             raise Exception("This class is a singleton!")
        else:
             ConnectionManager.__instance = self

    def connect(self, host='localhost', port=6666 , buf_size=1024):
         self.client = Client(host=host, port=port, buf_size=buf_size)

    def isOpen(self):
        return self.client.isOpen()
    
    def close(self):
        self.client.close()
                 
    def send(self, data):
        self.client.put_dict(data)

    def receive(self):
        recv = self.client.get_dict()
        return recv            
