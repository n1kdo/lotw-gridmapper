#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lotwreport.py: proxy for ARRL LoTW lotwreport.adi web service, which does not
support CORS headers and thus cannot be called from a script that is loaded
from any other server.  This CGI must be served from the same host name as
any script that wishes to call it.  Because I do not want other peoples'
scripts to call this service, it deliberately does not support CORS, either.
So don't try to call it on my server, it won't work.
"""
#
# LICENSE:
#
# Copyright (c) 2018, Jeffrey B. Otterson, N1KDO
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import cgi
import os
import urllib2

valid_args = ['login', 'password', 'qso_query', 'qso_qsl',
              'qso_qslsince', 'qso_qsorxsince', 'qso_owncall', 'qso_callsign',
              'qso_mode', 'qso_band', 'qso_dxcc',
              'qso_startdate', 'qso_starttime',
              'qso_enddate', 'qso_endtime',
              'qso_mydetail', 'qso_qsldetail', 'qso_withown']

form = cgi.FieldStorage()
callsign = form['login'].value if 'login' in form else None
password = form['password'].value if 'password' in form else None
client = os.environ["REMOTE_ADDR"]

pfx = '?'
url = 'https://lotw.arrl.org/lotwuser/lotwreport.adi'
for arg in valid_args:
    if arg in form:
        url = url + pfx + arg + '=' + form[arg].value
        pfx = '&'

if callsign.lower() == 'n1kdo' and password is None and client.startswith('192.168.1'):
    print 'Content-Type: application/x-arrl-adif'
    print
    try:
        filename = callsign + '.adi'
        with open(filename, 'r') as file:
            data = file.read()
        print data
    except IOError:
        print 'no cache'
else:
    req = urllib2.Request(url)
    response = urllib2.urlopen(req, None, 600)
    data = response.read()
    if callsign == 'n1kdo' and 'ARRL Logbook of the World Status Report' in data:
        filename = callsign.lower() + '.adi'
        with open(filename, 'w') as file:
            file.write(data)
    info = response.info()
    print 'Content-Type: %s' % info['Content-Type']
    print
    print data
