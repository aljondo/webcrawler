#!/usr/bin/python

import sys
import socket
import urlparse

#global stuff
login_form_url = 'http://fring.ccs.neu.edu/accounts/login/?next=/fakebook/'
fakebook_url = 'http://frint.ccs.neu.edu/fakebook'

username = '1922276'
password = 'Z53NLOS8'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)

visited = []
frontier = []

def get(url):
	new_url = urlparse.urlparse(url)
	#connect to the url at port 80
	s.connect((new_url.netloc, 80))
	s.send("GET / HTTP/1.1\r\n")
	
	print s.recv(4096)

def post():
	print "post"

def login():
	get(login_form_url)

def main():
	login()

main()