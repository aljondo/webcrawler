response = '''HTTP/1.1 200 OK
Date: Tue, 20 Mar 2018 01:13:39 GMT
Server: Apache/2.2.22 (Ubuntu)
Content-Language: en-us
Expires: Tue, 20 Mar 2018 01:13:39 GMT
Vary: Cookie,Accept-Language,Accept-Encoding
Cache-Control: max-age=0
Set-Cookie: csrftoken=ad6a84250d4e6764381a1406b50727ae; expires=Tue, 19-Mar-2019 01:13:39 GMT; Max-Age=31449600; Path=/
Set-Cookie: sessionid=f7655dbe258987483d554c1f06953f20; expires=Tue, 03-Apr-2018 01:13:39 GMT; Max-Age=1209600; Path=/
Last-Modified: Tue, 20 Mar 2018 01:13:39 GMT'''

for line in response.splitlines():
    if line.startswith('Set-Cookie: csrftoken='):
        csrftoken = line[22:54]
        print(csrftoken)
