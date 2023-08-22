# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/11_network.ipynb.

# %% auto 0
__all__ = ['Server', 'Client', 'ClientConnectionManager', 'ServerConnectionManager']

# %% ../nbs/11_network.ipynb 2
import socket
import json

# %% ../nbs/11_network.ipynb 3
class Server():
    def __init__(self, host='localhost', port=6666 , buf_size=1024):
        self.buf_size = buf_size
        self.host=host
        self.port=port
        self.listen()
            
    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Waiting for connection on {self.host}:{self.port}")
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
        length=-1
        lostconnection=False
        try:
            data = self.connection.recv(self.buf_size)
            length = len(data)
        except:
            lostconnection=True
            
        if lostconnection or length==0:
            self.listen()
            data = self.connection.recv(self.buf_size)
            
        dict = eval(data.decode())
        #print('recv',dict)
        return dict
    
    
    def put_dict(self, dict):
        #print('send',dict)       
        json_object = json.dumps(dict) 
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
        self.connection = socket.create_connection((host,port), timeout=120)
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
        #print("get ", dict)
        return dict
    
    def put_dict(self, dict):
        #print("send ", dict)
        json_object = json.dumps(dict) 
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
class ClientConnectionManager:
    "A utility for managing a client socket connection."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if ClientConnectionManager.__instance == None:
             ClientConnectionManager()
        return ClientConnectionManager.__instance
    
    def __init__(self, host='localhost', port=6666 , buf_size=1024):
        """ Virtually private constructor. """
        if ClientConnectionManager.__instance != None:
             raise Exception("This class is a singleton!")
        else:
             self.host='localhost'
             self.port=6666
             self.buf_size=1024
             self.connected=False
             ClientConnectionManager.__instance = self

    def connect(self):
        self.client = Client(host=self.host, port=self.port, buf_size=self.buf_size)
        self.connected=self.client.isOpen()

    def isOpen(self):
        return self.connected
    
    def close(self):
        self.client.close()
        self.connected=self.client.isOpen()
                 
    def send(self, data):
        if not self.isOpen():
            self.connect()
                
        self.client.put_dict(data)

    def receive(self):
        if not self.isOpen():
            self.connect()

        recv = self.client.get_dict()
        return recv            
    
    def set_port(self, port):
        self.port=port
        
    def set_host(self, host):
        self.host=host        

# %% ../nbs/11_network.ipynb 6
class ServerConnectionManager:
    "A utility for managing a client socket connection."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if ServerConnectionManager.__instance == None:
             ServerConnectionManager()
        return ServerConnectionManager.__instance
    
    def __init__(self, host='localhost', port=6666 , buf_size=1024):
        """ Virtually private constructor. """
        if ServerConnectionManager.__instance != None:
             raise Exception("This class is a singleton!")
        else:
             self.host='localhost'
             self.port=6666
             self.buf_size=1024
             self.connected=False
             ServerConnectionManager.__instance = self

    def connect(self):
        self.server = Server(host=self.host, port=self.port, buf_size=self.buf_size)
        self.connected=self.server.isOpen()

    def isOpen(self):
        return self.connected
    
    def close(self):
        self.server.close()
        self.connected=self.server.isOpen()
                 
    def send(self, data):
        if not self.isOpen():
            self.connect()
                
        self.server.put_dict(data)

    def receive(self):
        if not self.isOpen():
            self.connect()

        recv = self.server.get_dict()
        return recv            
    
    def set_port(self, port):
        self.port=port
        
    def set_host(self, host):
        self.host=host        
