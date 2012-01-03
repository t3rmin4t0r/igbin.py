<?php

$a = array(
	true, 
	false,
	1,
	-1,
	3.14567,
	"xyz",
	"xyz");

file_put_contents("array.ig", igbinary_serialize($a));
