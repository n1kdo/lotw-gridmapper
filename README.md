# lotw-gridmapper

`lotw-gridmapper` is a toy I made because I wanted it and 
I wanted to learn how to use Google Maps to display data.

There are two pieces.

* 6mGrids.html contains the just about everything except
* lotwaccess.php is a proxy that allows data to be downloaded
from Logbook Of The World without issues related to 
single-origin-policy issues accessing a 3rd party site from 
a web page.  It also converts the ADIF output into JSON which
is easier for the javascript on the web page to parse

If you decide to play with this, please get your own Google Maps
API Key.

I might do more work on this, or I might not.

n1kdo 20170701
