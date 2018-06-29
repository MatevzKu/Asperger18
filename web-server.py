#!/usr/bin/env python3
import ADC8032, NE555P, DS18B20, LCD16x2, time, os
from DS18B20 import read_temp
import socket as socket
import os, time
from random import random as rn

def normalize_line_endings(s):
     r'''Convert string containing various line endings like \n, \r or \r\n,
     to uniform \n.'''

     return ''.join((line + '\n') for line in s.splitlines())


MAX_PACKET = 32768

def recv_all(sock):
     r'''Receive everything from `sock`, until timeout occurs, meaning sender
     is exhausted, return result as string.'''

     # dirty hack to simplify this stuff - you should really use zero timeout,
     # deal with async socket and implement finite automata to handle incoming data

     prev_timeout = sock.gettimeout()
     try:
         sock.settimeout(0.01)

         rdata = []
         while True:
             try:
                 rdata.append(sock.recv(MAX_PACKET))
             except socket.timeout:
                 return ''.join(rdata)

         # unreachable
     finally:
         sock.settimeout(prev_timeout)

#host = socket.gethostname()
host = os.popen('ip addr show wlan0').read().split("inet ")[1].split("/")[0]
port = 8080

def serviraj():
     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s.bind((host,port))
     s.listen(1)
     counter=0
     ADC8032.init()
     while True:
         client_sock, client_addr = s.accept()
         print(client_sock)
         print(client_addr)
         #request = normalize_line_endings(recv_all(client_sock)) # hack again
         #request = recv_all(client_sock)
         #print (request)
         temp = read_temp()
         lux=ADC8032.getADC(0)
         lw, hi = NE555P.freq()
         freq = (1e+6/(lw+hi))
         client_sock.settimeout(None)
         response_body = '{"temp":' + str(temp) + ',"hum":' + str(freq) + ',"lum":' + str(lux) + '}'

         #response_body_raw = ''.join(response_body)

         # Clearly state that connection will be closed after this response,
         # and specify length of response body
         response_headers = {
             'Access-Control-Allow-Origin': '*',
             'Content-Type': 'text/html; encoding=utf8',
             'Content-Length': len(response_body),
             'Connection': 'close',
         }

         response_headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in response_headers.items())

         # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
         response_proto = 'HTTP/1.1'
         response_status = '200'
         response_status_text = 'OK' # this can be random

         # sending all this stuff
         client_sock.send(b'%s %s %s\r\n' % (str.encode(response_proto), str.encode(response_status), str.encode(response_status_text)))
         client_sock.send(str.encode(response_headers_raw))
         client_sock.send(str.encode('\r\n')) # to separate headers from body
         client_sock.send(str.encode(response_body))
         print("Sent!")
         # and closing connection, as we stated before
         time.sleep(0.5)
         client_sock.close()

if __name__ == '__main__':
   try:
     serviraj()
   except KeyboardInterrupt:
     pass
   finally:
     print("Bye")
