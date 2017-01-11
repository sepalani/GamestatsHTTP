# /web/client routes

## /upload.asp
*Not really a /web/client route, though*

### Example (Animal Crossing: Wild World)
```HTTP
POST /acrossingds/upload.asp HTTP/1.1
Host: gamestats.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
Content-Length: 822
Content-Type: application/x-www-form-urlencoded

pid=116434181111&hash=44a4d41fd81cad404f2596a3d4ec8fd31b2e74df&data=------------------------------------------------------------------------------------------------------------------8f8f------------------H-H------------------x-x------------------8f8f------------------H-H------------------x-x-x-x--------------8f8f8f8f--------------H-H-H-H--------------x-x-x-x--------------8f8f8f8f--------------H-H-H-H--------------x-x-x-x--------------8f8f8f8f--------------H-H-H-H------------------x-x--------------------n-n---------n5n5-----5-5---------5.Z.f----.Z.f----------n5n-----mf------------.Z.f--n5n-------------n5n5-5n5--------------.ZmZmZ-----------------5mZ.f---------------------------------------------------------------------------------------------bmQMpLSIbJwAA9Z0LHzAjKAAAAAAAHDEbGwAAAAAAAAAAAAAAAAAA1lwDDw**&region=eu
```
```HTTP
HTTP/1.1 200 OK
Date: Tue, 11 Mar 2014 11:56:26 GMT
Server: Microsoft-IIS/6.0
server: GSTPRDSTATSWEB2
X-Powered-By: ASP.NET
Content-Length: 0
Content-Type: text/html
Set-Cookie: ASPSESSIONIDQQCQDCSC=APHAMOCDPJFABHMPCINEJGLI; path=/
Cache-control: private
```


## /download.asp
*Not really a /web/client route, though*

### Example (Animal Crossing: Wild World)
#### Without Hash
```HTTP
GET /acrossingds/download.asp?pid=116434181111&region=eu HTTP/1.1
Host: gamestats.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Tue, 11 Mar 2014 11:56:27 GMT
Server: Microsoft-IIS/6.0
server: GSTPRDSTATSWEB2
X-Powered-By: ASP.NET
Content-Length: 32
Content-Type: text/html
Set-Cookie: ASPSESSIONIDQQCQDCSC=BPHAMOCDMMJNNDFBOINAIABC; path=/
Cache-control: private

9d3IIU533sVQ7sdKd0AanhAXgQyPI9fC
```

#### With Hash
```HTTP
GET /acrossingds/download.asp?pid=116434181111&hash=7960584475176fd6bd69a1a10f563b4ad50768a7&region=eu HTTP/1.1
Host: gamestats.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Tue, 11 Mar 2014 11:56:27 GMT
Server: Microsoft-IIS/6.0
server: GSTPRDSTATSWEB2
X-Powered-By: ASP.NET
Content-Length: 744
Content-Type: text/html
Set-Cookie: ASPSESSIONIDQQCQDCSC=CPHAMOCDPPGCFOJGLIKIFFCA; path=/
Cache-control: private

----qqqqqqqqqqqqqv-------6qqqqqqqqqqqvr---------qqqqqqqqqqr----------6.qqqqqqqr6------------qqqqqqqq-------------6.qqqqq.v---------------6qq-----------------------------------u7u7-----7u7.-------------v--7------------.-u--------7v7--------u7v7-----7.7.--------7u7u-----.7u7--------.7u--7--.-u-u--------9.7v-.---v5-7v--------fu7u-v--7.fu7v-------.-n5-----9.7u7--------vfu7-----7uf.---------.---------.---------------------------------------------------v--------------7-------7----------.---------v-----------.-------------4iI------------7.7---.P.P---.7.----------------------------7--v-.-.--7--v--------7--.7.7.7--.-------.---------------v---------------------------------------------fxR0pJikoIxsm9LAkGysvHyYjKAEAGyYbICwbKC0pGwAAAAAAAKAA6pEDAA**
```


## /put.asp
*TODO*

### Example (TODO)
```HTTP
/TODO/put.asp
```
```HTTP
HTTP/1.1 200 TODO
```


## /get.asp
*TODO*

### Example (TODO)
```HTTP
/TODO/get.asp
```
```HTTP
HTTP/1.1 200 TODO
```


## /put2.asp

### Example (Tatsunoko VS. Capcom: Ultimate All Stars)
#### Without Hash
```HTTP
GET /tatvscapwii/web/client/put2.asp?pid=249290728 HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sat, 07 May 2011 13:08:35 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
X-Powered-By: ASP.NET
cluster-server: gstprdweb12.las1.colo.ignops.com
X-Powered-By: ASP.NET
Content-Length: 32
Content-Type: text/html
Set-Cookie: ASPSESSIONIDCSBDTSCD=KOEKABKCPAPGEFONCEHADKEA; path=/
Cache-control: private

Eisq8fZ2s33Wriz3iku8rE9Tz1WgWh4x
```

#### With Hash
```HTTP
GET /tatvscapwii/web/client/put2.asp?pid=249290728&hash=a619fbb3a5fe6b680ae70a747dc2c747e256502d&data=aFtrRUhZ2g5cAAAA_wAAAAAAAABgHwAATAAAAAAACCsAAAAAAAADPwAADI4AAB9gAAAAAP__Izn__x4OAAD__wAAAAEAAAATAFMATQBUAEAARABEAFIAIAAgAAAAAAAAAAAAAAAAAAA= HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sat, 07 May 2011 13:08:35 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
X-Powered-By: ASP.NET
cluster-server: gstprdweb13.las1.colo.ignops.com
Content-Length: 44
Content-Type: text/html
Set-Cookie: ASPSESSIONIDQQCADDRC=FNGBCLJCKMKJGCDPPGCPGNJG; path=/
Cache-control: private

doneb7e684e8313b5729fd1c70a3fc19e425700449f6
```

## /get2.asp

### Example (TODO)
#### Without Hash
```HTTP
GET /TODO/get2.asp
```
```HTTP
HTTP/1.1 200 TODO
```

#### With Hash
```HTTP
GET /TODO/get2.asp
```
```HTTP
HTTP/1.1 200 TODO
```
