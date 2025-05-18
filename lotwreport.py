#!/bin/python3
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
# Copyright (c) 2018, 2023, 2025 Jeffrey B. Otterson, N1KDO
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

import argparse
import os
import urllib.error
import urllib.request
import sys
import traceback

valid_args = ('login', 'password', 'qso_query', 'qso_qsl',
              'qso_qslsince', 'qso_qsorxsince', 'qso_owncall', 'qso_callsign',
              'qso_mode', 'qso_band', 'qso_dxcc',
              'qso_startdate', 'qso_starttime',
              'qso_enddate', 'qso_endtime',
              'qso_mydetail', 'qso_qsldetail', 'qso_withown')


def get_request():
    # this is the endpoint for the cgi. it's really dumb.
    reading_headers = True
    headers = []
    body = []
    for line in sys.stdin:
        line = line.strip()
        if reading_headers:
            if len(line) == 0:
                reading_headers = False
            else:
                headers.append(line)
        else:
            body.append(line)
    qry = os.environ['QUERY_STRING']
    sq = qry.split('&')
    params = {}
    for field in sq:
        kv = field.split('=')
        if len(kv) == 2:
            params[kv[0]] = kv[1]

    client = os.environ.get('REMOTE_ADDR') or ''
    params['client'] = client

    return params


def call_lotw(params):
    callsign = params.get('login')
    password = params.get('password')
    client = params.get('client')

    pfx = '?'
    url = 'https://lotw.arrl.org/lotwuser/lotwreport.adi'
    for key in params.keys():
        if key in valid_args:
            url = url + pfx + key + '=' + params.get(key)
            pfx = '&'

    if password is None and client.startswith('192.168.1'):  # debugging hack for front end.
        print('Content-Type: application/x-arrl-adif')
        print('')
        try:
            filename = callsign + '.adi'
            with open(filename, 'r') as file:
                data = file.read()
            print(data)
        except IOError:
            print('no cache')
    else:
        try:
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, None, 600)
            data_bytes = response.read()
            data = data_bytes.decode('iso-8859-1')  # ,'ignore')
            if 'ARRL Logbook of the World Status Report' in data:
                filename = callsign.lower() + '.adi'
                with open(filename, 'w') as phile:
                    phile.write(data)
                info = response.info()
                print('Content-Type: %s' % info['Content-Type'])
                print('')
                print(data)
            elif '<I>Username/password incorrect</I>' in data:
                print('Content-Type: text/text')
                print('')
                print('Error: wrong username or password.')
        except Exception as e:
            print('Content-Type: text/text')
            print('')
            print(e)
            traceback.print_exc()


if __name__ == '__main__':
    if 'SCRIPT_NAME' in os.environ:
        params = get_request()
        call_lotw(params)
    else:
        parser = argparse.ArgumentParser(description='lotwreport.adi python LoTW Proxy')
        parser.add_argument('--login', required=True, type=str, help='lotw login name')
        parser.add_argument('--password', required=True, type=str, help='lotw login password')
        parser.add_argument('--qso_query', type=str, default='1', help='qso_query')
        parser.add_argument('--qso_qsl', type=str, default='yes', help='qso_qsl')
        parser.add_argument('--qso_qsldetail', type=str, default='yes', help='qso_qsl_detail')
        parser.add_argument('--qso_owncall', type=str, help='qso_owncall')
        parser.add_argument('--qso_callsign', type=str, help='qso_callsign')
        parser.add_argument('--qso_mode', type=str, help='qso_mode')
        parser.add_argument('--qso_band', type=str, help='qso_band')
        parser.add_argument('--qso_dxcc', type=str, help='qso_dxcc')
        parser.add_argument('--qso_startdate', type=str, default='2025-01-01', help='qso_startdate')
        parser.add_argument('--qso_starttime', type=str, help='qso_starttime')
        parser.add_argument('--qso_enddate', type=str, default='2025-06-30', help='qso_enddate')
        parser.add_argument('--qso_endtime', type=str, help='qso_endtime')
        parser.add_argument('--qso_qslsince', type=str, help='qso_qslsince')
        parser.add_argument('--qso_qsorxsince', type=str, help='qso_qslrxsince')
        parser.add_argument('--qso_withown', type=str, help='qso_withown')
        parser.add_argument('--qso_mydetail', type=str, help='qso_mydetail')
        parser.add_argument('--client', type=str, default='192.168.1.1', help='client ip address')
        args = parser.parse_args()
        cmd_line_params = {}
        for arg_name in valid_args:
            value = getattr(args, arg_name)
            if value is not None:
                cmd_line_params[arg_name] = value
        call_lotw(cmd_line_params)
