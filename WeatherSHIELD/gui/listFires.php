<?php
require 'connection.php';

$minLat = floatval($_GET['minLat']);
$maxLat = floatval($_GET['maxLat']);
$minLon = floatval($_GET['minLon']);
$maxLon = floatval($_GET['maxLon']);

$conn = connect($DFOSS_DATABASE);

$sql = "SELECT *"
        ." FROM [INPUTS].[ACTIVEFIRE]"
        ." ORDER BY FIRENAME ASC";

if ($conn){
    $outputArray = array();
    $stmt = try_query($conn, $sql);
    while( $row = sqlsrv_fetch_array( $stmt, SQLSRV_FETCH_ASSOC) ) {
        echo json_encode($row);
    }
}
else{
    echo("Error could not connect to SQL database: ".print_r( sqlsrv_errors(), true));
}

/* Close the connection. */
sqlsrv_close( $conn);
?>