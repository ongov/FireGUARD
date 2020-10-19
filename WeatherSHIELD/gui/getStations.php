<?php
require 'connection.php';

$minLat = floatval($_GET['minLat']);
$maxLat = floatval($_GET['maxLat']);
$minLon = floatval($_GET['minLon']);
$maxLon = floatval($_GET['maxLon']);

$conn = connect($DFOSS_DATABASE);

$sql = "SELECT WSTNCODE, LATITUDE, LONGITUDE"
        ." FROM [INPUTS].[CT_WSTN]"
        ." WHERE 0=0"
        ." AND WSTNCODE NOT LIKE '4%'"
        .($minLat ? " AND LATITUDE >=".$minLat : "")
        .($maxLat ? " AND LATITUDE <=".$maxLat : "")
        .($minLon ? " AND LONGITUDE >=".$minLon : "")
        .($maxLon ? " AND LONGITUDE <=".$maxLon : "")
        ." ORDER BY WSTNCODE ASC";

if ($conn){
    $outputArray = array();
    $stmt = try_query($conn, $sql);
    while( $row = sqlsrv_fetch_array( $stmt, SQLSRV_FETCH_ASSOC) ) {
        $outputArray[$row['WSTNCODE']] = array(
                        floatval($row['LATITUDE']),
                        floatval($row['LONGITUDE']),
                    );
    }
    echo json_encode($outputArray);
}
else{
    echo("Error could not connect to SQL database: ".print_r( sqlsrv_errors(), true));
}

/* Close the connection. */
sqlsrv_close( $conn);
?>