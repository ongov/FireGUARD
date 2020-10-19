<?php
$WX_DATABASE = 'WX_'.date('Ym');
$DFOSS_DATABASE = 'DFOSS_'.date('Y');

function connect($db)
{
    $conn_array = array (
        "UID" => "wx_readonly",
        "PWD" => "wx_r34d0nly!",
        "Database" => $db,
    );
    $serverName = ".\sqlexpress";

    return sqlsrv_connect( $serverName, $conn_array);
}

function try_query($conn, $sql)
{
    $stmt = sqlsrv_query($conn,$sql);
    if( $stmt === false) {
        echo("Error could not run SQL command: ".$sql."\n".print_r( sqlsrv_errors(), true));
        die;
    }
    return $stmt;
}

$conn = connect($DFOSS_DATABASE);
if ($conn){
/* Close the connection. */
sqlsrv_close($conn);
}
else{
    echo("Error could not connect to SQL database: ".print_r( sqlsrv_errors(), true));
    exit();
}

?>
