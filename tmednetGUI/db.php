<?php
$host = '172.16.0.44:3306';
$username = 'tmednetj382';
$password = '$eE%q0l32';
$db = 'tmednetj382';

session_start();

$link = mysqli_connect($host, $username, $password, $db) or die("Aterkia - Connection failed: " . mysqli_connect_error());

if (mysqli_connect_errno()) {
	printf("Aterkia - Connect failed: %s\n", mysqli_connect_error());
	exit();
}
?>