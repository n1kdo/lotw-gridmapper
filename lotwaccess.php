<?php
/*
lotwaccess.php: proxy/json converter for ARRL LoTW lotwreport.adi web service.

LICENSE:

Copyright (c) 2017, Jeffrey B. Otterson, N1KDO
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

function parseAdifLine($line) {
    preg_match("/<(.*)>(.*)/", $line, $matches);
    $result = array();
    if (count($matches) > 1) {
        $temp = $matches[1];
        preg_match("/(.*):.*/", $temp, $match2);
        if (count($match2) > 1) {
            $result[0] = $match2[1];
        } else {
            $result[0] = $matches[1];
        }
        if (count($matches) > 2 && strlen($matches[2]) > 0) {
            $result[1] = $matches[2];
        }
    }
    return $result;
}
header("Content-type: text/text");
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
error_log("url: " . $url);
$login = $_REQUEST['login'];
if ($login === 'xxxn1kdo') {
    $url = 'lotwreport.adi'; // DEBUG FIXME!
    error_log('debug local file mode');
}
$firstLine = true;
$qso = Array();
$qsos = Array();

$response = file_get_contents($url);
error_log("got data back from lotw");
$keepgoing = true;
$separator = "\r\n";
$line = trim(strtok($response, $separator));
while ($line !== false && $keepgoing === true) {
    if ($firstLine === true) {
        $firstLine = false;
        if ($line !== "ARRL Logbook of the World Status Report") {
            error_log("LOTW failure Reply: " . $line);
            header("HTTP/1.1 403 Forbidden");
            header("Status: 403 Forbidden");
            echo "401 Forbidden\n\n";
            echo "Did not get expected response from lotw web service.\n\n";
            echo "got:\n\n";
            echo $line . "\n\n";
            echo "--\n";
            $keepgoing = false;
        }
    } else {
        $foo = parseAdifLine($line);
        if (count($foo) == 1) {
            if ($foo[0] === "eor") {
                $qsos[] = $qso;
                $qso = Array();
            }
            if ($foo[0] === "eoh") {
                $qso = Array();
                $qsos = Array();
            }
        }
        if (count($foo) == 2) {
            $key = strtolower($foo[0]);
            $qso[$key] = $foo[1];
        }
    }
    $line = strtok($separator);
}
header("Content-type: text/text");
echo json_encode($qsos);
?>