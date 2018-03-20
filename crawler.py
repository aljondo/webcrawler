#!/usr/bin/python

import sys
import socket
import urlparse
from HTMLParser import HTMLParser

#global stuff
login_form_url = 'http://fring.ccs.neu.edu/accounts/login/?next=/fakebook/'
fakebook_url = 'http://fring.ccs.neu.edu/fakebook'

username = '1922276'
password = 'Z53NLOS8'

csrf_token = ""
sessionid = ""

#SAT: slashes_and_things
SAT = "\r\n\r\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)

visited = []
frontier = []

def get(url):
	new_url = urlparse.urlparse(url)
	#connect to the url at port 80
	s.connect((new_url.netloc, 80))
	s.send("GET " + new_url.path + "/ HTTP/1.1\r\nHOST: " + new_url.netloc +"\r\n\r\n")
	
	data = s.recv(4096)
	#s.shutdown(1)
	#s.close()
	return parse_page(data)

def post(url, content):
	global csrf_token
	global sessionid
	new_url = urlparse.urlparse(url)

	head = "POST " + new_url.path + " HTTP/1.1\r\n"
	host = "Host: " + new_url.netloc + "\r\n"
	content_type = "Content-Type: application/x-www-form-url\r\n"
	content_length = "Content-Length: " + str(len(content)) + "\r\n"
	cookie = "Cookie: csrftoken=" + csrf_token + "; sessionid=" + sessionid + SAT
	msg = head + host + content_type + content_length + cookie + content
	
	print msg
	s.send(msg)
	#post for login purposes
	print "post"
	print s.recv(4096)

def parse_page(data):
	global csrf_token
	global sessionid
	data = data.split("\r\n\r\n")
	header = data[0].split("\r")
	header_table = {}
	#get session stuff
	print "PLS"
	for x in header:
		line = x.split(": ")
		if len(line) == 2 and line[0][1:] == 'Set-Cookie':
			if 'csrftoken' in line[1]:
				csrf_token = line[1].split(';')[0].split('=')[1]
			elif 'sessionid' in line[1]:
				sessionid = line[1].split(';')[0].split('=')[1]
		#if line[1] and line[0][1:] == 'set'
	#print header_table['set-cookie']
	return data

def login():
	get(login_form_url)
	#construct post
	p_msg = "username=" + username + "&password=" + password + "&csrfmiddlewaretoken=" + csrf_token + "&next=/fakebook/"
	post(login_form_url, p_msg)

def main():
	login()

main()