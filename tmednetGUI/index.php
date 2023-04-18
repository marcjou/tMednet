<?php 
include_once("db.php");

$sql = "SELECT * FROM jos_users ORDER BY id";

$result = mysqli_query($link, $sql) or die("Database error: ". mysqli_error($link));

mysqli_close($link);

while( $rows = mysqli_fetch_assoc($result)){
	$html_users_table.= "<div style='padding:3em 0'>"."\n";
    $html_users_table.= "\t"."<div style='border:1px dotted red'>ID: ".$rows['id']."</div>"."\n";
    $html_users_table.= "\t"."<div style='border:1px dotted red'>Name: ".$rows['name']."</div>"."\n";
    $html_users_table.= "\t"."<div style='border:1px dotted red'>E-mail: ".$rows['email']."</div>"."\n";
    $html_users_table.= "</div>"."\n";
}
?>

<!DOCTYPE html>
<html>

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Marc</title>
<link href="assets/favicon.ico" rel="shortcut icon" type="image/x-icon" /> 
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.css">
<link href="assets/style.css" rel="stylesheet">
</head>

<body style="background:white;">

<div class="container">
	<?php echo $html_users_table; ?>
</div>

<script src='http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>
<script src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'></script>
<script src="assets/carousel-slider.js"></script>

</div>
</div>

</body>

</html>
