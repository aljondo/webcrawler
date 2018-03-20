#!/usr/bin/python3
import sys
import socket
from bs4 import BeautifulSoup

username = sys.argv[1]
password = sys.argv[2]

host = 'fring.ccs.neu.edu'
root_site = 'http://' + host
root_page = root_site + '/fakebook/'
login_page = root_site + '/accounts/login/'

http_version = '1.0'

csrftoken = ''
sessionid = ''

explored = []
unexplored = []

secret_flags = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 80))

def getSafeLink(url):
    if url.startswith(root_site):
        return url[len(root_site):]
    return url

def checkResponse(response):
    global csrftoken, sessionid
    if 'Set-Cookie:' in response:
        for line in response.splitlines():
            if line.startswith('Set-Cookie: csrftoken='):
                csrftoken = line[22:54]
            elif line.startswith('Set-Cookie: sessionid='):
                sessionid = line[22:54]

def getRequest(route):
    request =  ('GET ' + route + ' HTTP/' + http_version + '\n'
                'Host: ' + host + '\n\n')
    print('GET request:')
    print(request)
    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')
    print('GET response:')
    print(response)

    checkResponse(response)

    html = response.split('\n\n', 1)[-1]
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def getLoginToken():
    login_soup = getRequest(getSafeLink(login_page))
    token = login_soup.find_all(attrs={"name": "csrfmiddlewaretoken"})[0]['value']
    return token


def postLogin():
    # token = getLoginToken()
    # content = 'username=' + username + '&password=' + password + '&csrfmiddlewaretoken=' + token + '&next=/fakebook/'
    getRequest(getSafeLink(login_page))
    content = 'username=' + username + '&password=' + password + '&csrfmiddlewaretoken=' + csrftoken + '&next=/fakebook/'
    request =  ('POST ' + getSafeLink(login_page) + ' HTTP/' + http_version + '\n'
                'Host: ' + host + '\n'
                'Cookie: ' + 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '\n'
                'Content-Type: application/x-www-form-urlencoded\n'
                'Content-Length: ' + str(len(content)) + '\n\n'
                '' + content + '\n\n')
    print('POST request:')
    print(request)
    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')
    print('POST response:')
    print(response)

    checkResponse(response)



# Send POST request to login_page with id_username = username and id_password = password
postLogin()
# getRequest(getSafeLink(login_page))
# On 200, get current page (should be root_page) and add it to unexplored


while len(unexplored) > 0:
    # Pop first element from unexplored
    current_page = unexplored.pop()
    soup = getRequest(current_page)

    anchors = soup.find_all('a')
    h2s = soup.find_all('h2')
    # Get tags from current_page
    # for tag in tags:
    #     # If tag is an anchor and that anchor has not been explored, add it to unexplored
    #     if tag['type'] == 'a' and tag['href'] not in explored:
    #         unexplored.append(tag['href'])
    #
    #     # If tag is an h2 and has class of 'secret_flag', add its contents to secret_flags
    #     elif tag['type'] == 'h2' and tag['class'] == 'secret_flag':
    #         secret_flags.append(tag['content'])

    # Add current_page to explored
    explored.append(current_page)

print('Secret flags:', secret_flags)
