#!/usr/bin/python3
import sys
import socket
from bs4 import BeautifulSoup

#username = sys.argv[1]
#password = sys.argv[2]
username = '1922276'
password = 'Z53NLOS8'

host = 'fring.ccs.neu.edu'
root_site = 'http://' + host
root_page = root_site + '/fakebook/'
login_page = root_site + '/accounts/login/'

http_version = '1.1'

csrftoken = ''
sessionid = ''
logged_in = False

explored = []
unexplored = ['/fakebook/']

secret_flags = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 80))

def getSafeLink(url):
    if url.startswith(root_site):
        return url[len(root_site):]
    return url

#sets cookies and also returns the status
def checkResponseHeader(response):
    global s
    global csrftoken, sessionid
    if 'Set-Cookie:' in response:
        for line in response.splitlines():
            if line.startswith('Set-Cookie: csrftoken='):
                csrftoken = line[22:54]
            elif line.startswith('Set-Cookie: sessionid='):
                sessionid = line[22:54]
    status = response.split("\r")[0].split(" ")
    print(" c h e c k r e p o n s e h e a d er ")
    #print(response)
    if len(status) == 3:
        print(response.split("\r\n\r\n")[0]) #<- print header in case somethings weird
        status = status[1]
    else:
        print("something is going wrong here. this is the response:")
        print(response)
        status = "something_is_wrong"
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))
    return status

def getRequest(route):
    global csrftoken, sessionid, s
    #add cookies to request if they're there
    cookie = "in"
    if len(csrftoken) > 0:
        cookie = "Cookie: csrftoken=" + csrftoken + "; sessionid=" + sessionid + "\r\n"
        request =  ('GET ' + route + ' HTTP/' + http_version + '\r\n'
                    'Host: ' + host + '\r\n'
                    'Cookie: csrftoken=' + csrftoken + "; sessionid=" + sessionid + '\r\n\r\n')
    else:
        request = ('GET ' + route + ' HTTP/' + http_version + '\r\n'
                    'Host: ' + host + '\r\n\r\n')
    print('GET request:')
    print(request)
    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')
    #print('GET response:')
    #print(response)

    status = checkResponseHeader(response)
    #print("WHAT IS THE STATUS OF THIS GET REQUEST")
    #print(status)
    if status == '200':
        #add route to explored
        explored.append(route)
    elif status == '301':
        #TODO
        print("WE GOT US A 301 LADS ESKETIT")
    elif status == '403' or status == '404':
        if len(unexplored) == 0:
            #this means there's nothing left to explore. return False so the crawler knows
            return False
        else:
            #add route to explored, get the next route from the frontier and get that
            explored.append(route)
            getRequest(unexplored.pop())
    else:
        #this means the status is 500, or something's going weirdly wrong.
        #in both cases, we wanna try again with the same route anyway
        getRequest(route)
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
    global s
    getRequest(getSafeLink(login_page))
    content = 'username=' + username + '&password=' + password + '&csrfmiddlewaretoken=' + csrftoken + '&next=/fakebook/'
    request =  ('POST ' + getSafeLink(login_page) + ' HTTP/' + http_version + '\n'
                'Host: ' + host + '\n'
                'Cookie: ' + 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '\n'
                'Content-Type: application/x-www-form-urlencoded\n'
                'Content-Length: ' + str(len(content)) + '\n\n'
                '' + content + '\n\n')
    s.send(request.encode('ascii'))
    response = s.recv(4096).decode('ascii')
    #print("POST response")
    #print(response)
    status = checkResponseHeader(response)
    if status == '302':
        #print("we made it")
        logged_in = True
    else:
        #print("trying again")
        postLogin()
    return True
    
# getRequest(getSafeLink(login_page))
# On 200, get current page (should be root_page) and add it to unexplored

def crawl():
    while len(unexplored) > 0:
        # Pop first element from unexplored
        current_page = unexplored.pop()
        soup = getRequest(current_page)
        if not soup:
            #got a 404, and there are no more links in the frontier
            break
        #print("THE SOUP")
        #print(soup) 
        anchors = soup.find_all('a')
        h2s = soup.find_all('h2')
        
        #print("anchors")
        #print(anchors)
        #print("headers")
        #print(h2s)
        
        for a in anchors:
            if a['href'] not in explored and a['href'] not in unexplored:
                if a['href'][:1] == '/' or a['href'][:25] == 'http://fring.ccs.neu.edu/':
                    unexplored.append(a['href'])
        #print("new frontier")
        #print(unexplored)
        for h in h2s:
            if 'class' in h and h['class'] == 'secret_flag':
                secret_flags.append(tag['content'])
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


#if postLogin returns true aka it got a 302, then begin crawl
if postLogin():
    crawl()
s.close()
print('Secret flags:', secret_flags)
