#!/usr/bin/python3
import sys
import socket
from bs4 import BeautifulSoup

username = str(sys.argv[1])
password = str(sys.argv[2])

host = 'fring.ccs.neu.edu'
root_site = 'http://' + host
root_page = root_site + '/fakebook/'
login_page = root_site + '/accounts/login/'

http_version = '1.1'

csrftoken = ''
sessionid = ''
next_location = ''
logged_in = False

explored = []
unexplored = ['/fakebook/']

secret_flags = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 80))

# Given a link, make sure it is relative and not absolute
def getSafeLink(url):
    if url.startswith(root_site):
        return url[len(root_site):]
    return url

# Given an HTTP response, set the appropriate cookies and return the status
def checkResponseHeader(response):
    global s, csrftoken, sessionid, location
    if 'Set-Cookie:' in response:
        for line in response.splitlines():
            if line.startswith('Set-Cookie: csrftoken='):
                csrftoken = line[22:54]
            elif line.startswith('Set-Cookie: sessionid='):
                sessionid = line[22:54]
            elif line.startswith('Location:'):
                location = line.split(" ")[1]
    status = response.split("\r")[0].split(" ")

    if len(status) >= 3:
        status = status[1]
    else:
        status = " ".join(status)
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))
    return status

# Given a relative path, send a GET request for the page and return the BeautifulSoup object of that page
def getRequest(route):
    global csrftoken, sessionid, s

    # Add cookies to request if they're there
    cookie = "in"
    if len(csrftoken) > 0:
        cookie = "Cookie: csrftoken=" + csrftoken + "; sessionid=" + sessionid + "\r\n"
        request =  ('GET ' + route + ' HTTP/' + http_version + '\r\n'
                    'Host: ' + host + '\r\n'
                    'Cookie: csrftoken=' + csrftoken + "; sessionid=" + sessionid + '\r\n\r\n')
    else:
        request = ('GET ' + route + ' HTTP/' + http_version + '\r\n'
                    'Host: ' + host + '\r\n\r\n')

    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')

    # Check for bad responses
    while response == '0\r\n\r\n':
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))
        s.send(request.encode('ascii'))
        response = s.recv(4096).decode('ascii')

    status = checkResponseHeader(response)

    # If the transfer is chunked and incomplete, keep receiving (as long as the status is 200)
    while 'Transfer-Encoding: chunked' in response and '</html>' not in response and status == '200':
        response += s.recv(4096).decode('ascii')
        status = checkResponseHeader(response)

    if status == '200':
        explored.append(route)
    elif status == '301':
        explored.append(route)
        if next_location[:25] == 'http://fring.ccs.neu.edu/':
            return getRequest(next_location[25:])
        elif next_location[:1] == '/':
            return getRequest(next_location)
        else:
            return getRequest(unexplored.pop())
    elif status == '403' or status == '404':
        if len(unexplored) == 0:
            # This means there's nothing left to explore. return False so the crawler knows
            return False
        else:
            # Add route to explored, get the next route from the frontier and get that
            explored.append(route)
            return getRequest(unexplored.pop())
    else:
        # This means the status is 500, or something's going weirdly wrong.
        # In both cases, we wanna try again with the same route anyway
        return getRequest(route)
    html = response.split('\r\n\r\n', 1)[-1]
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# Login to Fakebook through a POST request
def postLogin():
    global s
    # Make an intial GET request to set the cookies
    getRequest(getSafeLink(login_page))

    # Set up the POST request
    content = 'username=' + username + '&password=' + password + '&csrfmiddlewaretoken=' + csrftoken + '&next=/fakebook/'
    request =  ('POST ' + getSafeLink(login_page) + ' HTTP/' + http_version + '\n'
                'Host: ' + host + '\n'
                'Cookie: ' + 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '\n'
                'Content-Type: application/x-www-form-urlencoded\n'
                'Content-Length: ' + str(len(content)) + '\n\n'
                '' + content + '\n\n')
    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')

    status = checkResponseHeader(response)

    if status == '302':
        logged_in = True
    else:
        postLogin()
    return True


def crawl():
    while len(unexplored) > 0:
        # Pop first element from unexplored
        current_page = unexplored.pop()
        soup = getRequest(current_page)
        if not soup:
            # Got a 404, and there are no more links in the frontier
            break

        # Extract and handle <a> tags
        anchors = soup.find_all('a')
        for a in anchors:
            if a['href'] not in explored and a['href'] not in unexplored:
                if a['href'][:1] == '/' or a['href'][:25] == 'http://fring.ccs.neu.edu/':
                    unexplored.append(a['href'])

        # Extract and handle <h2> tags (to find flags)
        h2s = soup.find_all('h2')
        for h in h2s:
            text = h.contents[0]
            if 'FLAG:' in text:
                flag = text.split(" ")[1]
                if flag not in secret_flags:
                    secret_flags.append(flag)
                    if len(secret_flags) == 5:
                        for secret_flag in secret_flags:
                            print(secret_flag)
                        sys.exit(1)

# If postLogin returns true (aka it got a 302), then begin crawl
if postLogin():
    crawl()
s.close()
