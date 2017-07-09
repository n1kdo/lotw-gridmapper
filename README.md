# lotw-gridmapper

![Example](n1kdo-6m-grids.png)

`lotw-gridmapper` is a toy I made because I wanted it and 
I wanted to learn how to use Google Maps to display data.

There are two pieces.

* 6mGrids.html contains the just about everything except

* lotwaccess.php is a proxy and json converter
 
lotwaccess.php provides a proxy (to work around the browser's 
single-origin policy) that also converts the ADIF returned 
from the Logbook Of The World web service into JSON data,
which is much easier to work with in JavaScript.  

If you decide to play with this, please get your own Google Maps
API Key.

I might do more work on this, or I might not.

n1kdo 20170701
