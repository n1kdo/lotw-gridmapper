<?php
/*
lotwreport.php: proxy for ARRL LoTW lotwreport.adi web service to avoid browser issues with
Single-Origin Policy.  Serves web service from the same host as the script.

LICENSE:

Copyright (c) 2018, Jeffrey B. Otterson, N1KDO
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

$valid_args = array('login', 'password', 'qso_query',  'qso_qsl',
    'qso_qslsince', 'qso_qsorxsince', 'qso_owncall', 'qso_callsign',
    'qso_mode', 'qso_band', 'qso_dxcc',
    'qso_startdate', 'qso_starttime',
    'qso_enddate', 'qso_endtime',
    'qso_mydetail', 'qso_qsldetail', 'qso_withown');
$url = 'https://lotw.arrl.org/lotwuser/lotwreport.adi';
$argprefix = '?';
foreach ($valid_args as &$a) {
    if(isset($_REQUEST[$a])){
        $d = $_REQUEST[$a]; // escape/validate?
        $url .= $argprefix . $a . '=' . $d;
        $argprefix = '&';
    }
}
# error_log("url: " . $url);
$login = strtolower($_REQUEST['login']);
$password = $_REQUEST['password'];
$client = $_SERVER['REMOTE_ADDR'];
$http_response_header = array("HTTP/1.1 200 OK",
    "Content-Type: application/x-arrl-adif",
);
if ((strncmp("192.168.1.", $client,10) === 0) && $password === '') { // look for my cached adif
    $response = file_get_contents($login . '.adi');
    error_log('debug local file mode');
} else {
    $response = @file_get_contents($url) or "";
    if (strlen($response) > 0 && strpos($response, 'ARRL Logbook of the World Status Report') === 0) {
        if (true || strtolower($login) === 'n1kdo') { // cache my ADIF
            $fp = fopen(strtolower($login) . '.adi', 'w');
            if ($fp) {
                fwrite($fp, $response);
                fclose($fp);
            }
        }
    }
}
foreach ($http_response_header as $header) {
    header($header);
}
echo $response;
?>
