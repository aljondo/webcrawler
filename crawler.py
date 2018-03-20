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

logged_in = False
visited = []
frontier = []

def get(url):
	print "GET"
	global logged_in
	new_url = urlparse.urlparse(url)
	s.connect((new_url.netloc, 80)) #TODO: can't do this everytime unless i'm planning on closing the socket

	head = "GET " + new_url.path + " HTTP/1.1\r\n"
	host = "HOST: " + new_url.netloc
	get_message = head + host + SAT
	s.send(get_message)
	data = s.recv(4096)
	#s.shutdown(1)
	#s.close()
	status = parse_header(data)
	if logged_in:
		parse_page(data)

	return parse_page(data)

def post(url, content):
	global csrf_token
	global sessionid
	global logged_in
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
	data = s.recv(4096)
	status = parse_header(data)
	if status == "302":
		logged_in = True
	else:
		post(url, content) #try again

	return True

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

#sets cookies and returns status
def parse_header(data):
	global csrf_token
	global sessionid
	header = data.split("\r\n\r\n")[0].split("\r")
	status = header[0].split(" ") #status number
	if len(status) == 3:
		status = status[1]
	else:
		status = "something didnt work lol"
	for x in header:
		line = x.split(": ")
		if len(line) == 2 and line[0][1:] == 'Set-Cookie':
			if 'csrftoken' in line[1]:
				csrf_token = line[1].split(';')[0].split('=')[1]
			elif 'sessionid' in line[1]:
				sessionid = line[1].split(';')[0].split('=')[1]
	return status

def login():
	get(login_form_url)
	#construct post
	p_msg = "username=" + username + "&password=" + password + "&csrfmiddlewaretoken=" + csrf_token + "&next=/fakebook/"
	
	if post(login_form_url, p_msg):
		get(fakebook_url)

def main():
	login()

main()