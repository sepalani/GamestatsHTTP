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

### Example (Mario Strikers Charged Football)
#### Without Hash
```HTTP
GET /mschargedwii/web/client/put2.asp?pid=355776439 HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sun, 18 May 2014 11:44:50 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
cluster-server: gstprdweb13.las1.colo.ignops.com
X-Powered-By: ASP.NET
Content-Length: 32
Content-Type: text/html
Set-Cookie: ASPSESSIONIDCATBCDCD=PHKJJNEAEICIGKFNNMFMECDD; path=/
Cache-control: private

yTeitsg1L1AD5u8bmx5T8VpS9QK7vNGX
```

#### With Hash
```HTTP
GET /mschargedwii/web/client/put2.asp?pid=355776439&hash=a991ad96336e6ebcbdef5676f140a300a2a7b5de&data=QttED7e3NBWQAAAABAAAAAIAAAAQAAAAgAAAABIFB94AAAABAAAAAgACAHMAZQBiAAD_Vf3I-8MAqv9V_cj746hWAHMAZQBiAAAAAAAAAAAAAAAAAAB_UYB2N3fCXLmQIAxmAAGWCKIIjAhANEiYjTCKAIolBQAAAAAAAAAAAAAAAAAAAAAAAAAAlveDTEEndGCCEhX5wMekPim2 HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sun, 18 May 2014 11:44:51 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
cluster-server: gstprdweb15.las1.colo.ignops.com
X-Powered-By: ASP.NET
Content-Length: 44
Content-Type: text/html
Set-Cookie: ASPSESSIONIDSASRSATD=PIJLNNEAAAOKNLBLLBDAGGMP; path=/
Cache-control: private

done15a5ff3d835a9e893af615959c78552ac0f02909
```

## /get2.asp

### Example (Mario Strikers Charged Football)
#### Without Hash
```HTTP
GET /mschargedwii/web/client/get2.asp?pid=355776439 HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sun, 18 May 2014 11:45:27 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
cluster-server: gstprdweb16.las1.colo.ignops.com
X-Powered-By: ASP.NET
Content-Length: 32
Content-Type: text/html
Set-Cookie: ASPSESSIONIDQARTQDSD=JMPBHIEAJJNNMLDOBKIFDFIL; path=/
Cache-control: private

KQkQRfx1anLfWgPFbAgL1hWLsKkUK8T8
```

#### With Hash
```HTTP
GET /mschargedwii/web/client/get2.asp?pid=355776439&hash=4e2a8b441d4caba5222639f0b1a3952dd0c1d288&data=QttiWbe3NBUcAAAABAAAAAEAAAACAAAADAAAAAEAAAAKAAAAwgIAAA== HTTP/1.1
Host: gamestats2.gs.nintendowifi.net
User-Agent: GameSpyHTTP/1.0
Connection: close
```
```HTTP
HTTP/1.1 200 OK
Date: Sun, 18 May 2014 11:45:28 GMT
Server: Microsoft-IIS/6.0
p3p: CP='NOI ADMa OUR STP'
cluster-server: gstprdweb13.las1.colo.ignops.com
X-Powered-By: ASP.NET
Content-Length: 1572
Content-Type: text/html
Set-Cookie: ASPSESSIONIDSQQQSRAS=FJPKFMEAHKEFLFCEDPCBNNEK; path=/
Cache-control: private

....
.......I.....4................................s.e.b...U.......U.....V.s.e.b...............Q.v7w.\.. .f........@4H..0...%........................LA't`.......>).....'a.......................................?.?.?&....U.....%............&....R..;<..#.'.....H`1.(....@.I......%..r.a.f.a.e.l............S>.svz.............`.................................b...b... .m.a.r.i.o...
.b...b... .m.a.r.i.o.....1Yp1.`-JL).(.P..A.I(...q
.......................x....?B^%h....IH......c.................................l.i.l.i.a.n.....U.....a.l.i.l.i.a.n...o.s.s....O.YY....b.1...<..H.Mx.....%..l.i.l.i..............wC
...T...+. .W........................................J.a.n. .G.o.l.d......
..J.a.n. .G.o.l.d....+.....A.....D\..(....T.I......%........................u.c.O&.....b.......^.c.........a......................J.A.V.I.........U.......J.A.V.I.............L..ctA.....b@1.(....@.I..t...%.......................X..7.....D.....B......................................&..S.c.a.r.t&....U......&..S.c.a.r.t&.......@...f....v4.C.2=.h...\.M.
....%.&..B.G&...............f|.v.L....}..Tc.....S/..
.......v......................e.t.h.a.n. .w. &.&....!.e.t.h.a.n. .w. &.&.T1..
.G.....>@1.(....@.Mx.....%.......................}......]..5L..5.....,...
.......7......................g.u.-.g.u.s.....U....*a.g.u.-.g.u.s........5...c.h0....BZ..(...HD.H......%..m.a.r.i.u.s..........#...}E...:...U;.......B................................M.a.i.t.r.e.G.i.m.s.....M.a.i.t.r.e.G.i.m.s3K..5e.
.:4.Z@1.(....@.M0.`...%........................G..0-@.O..0;.d.0551fef291adc9ca4f96469db0afa5b34911f887
```
[Network dump](https://www.cloudshark.org/captures/82bb137e8990)
