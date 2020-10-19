<?php
require 'connection.php';

$conn = connect("WXSHIELD");

$sql = "SELECT *"
        ." FROM [LOG].[FCT_Forecast]"
        ." ORDER BY [Latitude], [Longitude], [Offset], [NumDays], [Timeof]";

date_default_timezone_set('America/New_York');

if ($conn){
    $outputArray = array();
    $stmt = try_query($conn, $sql);
    $tz_offset = date('Z') / 60 / 60;
    while( $row = sqlsrv_fetch_array( $stmt, SQLSRV_FETCH_ASSOC) ) {
      // HACK: changes value of row but doesn't actually matter in the end
      $utc_time = $row['Timeof']->setTimezone(new DateTimeZone("UTC"));
      $cur_array = array(
                    'IP' => $row['IP'],
                    'Timeof' => date_format($utc_time, 'Y-m-d\TH:i:s').'.000Z',
                    'Latitude' => $row['Latitude'],
                    'Longitude' => $row['Longitude'],
                    'Offset' => $row['Offset'],
                    'NumDays' => $row['NumDays'],
                    'Query' => $row['Query']
      );
      array_push($outputArray, $cur_array);
    }
    echo json_encode($outputArray);
}
else{
    echo("Error could not connect to SQL database: ".print_r( sqlsrv_errors(), true));
}

/* Close the connection. */
sqlsrv_close( $conn);
?>
