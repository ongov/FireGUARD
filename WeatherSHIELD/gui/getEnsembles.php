<?php
require 'connection.php';


function setStart($offSet){
    $theStart = new DateTime('now');
    date_add($theStart, date_interval_create_from_date_string($offSet. " days"));
    return $theStart;
}


// round to this many digits because otherwise it's overkill
$lat = floatval($_GET['lat']);
$long = floatval($_GET['long']);
$offset = intval($_GET['dateOffset']);
$startDate = setStart($offset);
$numDays = strval($_GET['numDays']);

function modelArray($last_row, $membersArray)
{
    if(is_null($last_row['Generated']))
    {
        echo('No historic match data exists');
        exit();
    }
    return array(
            // these are all Zulu times
            "Generated" => date_format($last_row['Generated'], 'Y-m-d\TH:i:s').'.000Z',
            "lat"=>$last_row['Latitude'],
            "lon"=>$last_row['Longitude'],
            // this is in meters, so no decimal digits should be fine
            "DistanceFrom" => round($last_row['DISTANCE_FROM']),
            "Members" => $membersArray
        );
}

function roundValue($value)
{
    // NOTE: idn't work with this as a global variable (rounded to 0 digits)
    $num_digits = 2;
    return round($value, $num_digits);
}

function getStartup($conn_dfoss, $offset, $lat, $long)
{
    // uses observed from yesterday
    $sql_startup = 'SELECT * FROM [INPUTS].[FCT_FWIObserved_By_Offset]('.($offset - 1).', '.$lat.', '.$long.', DEFAULT)';
    $stmt_startup = try_query($conn_dfoss, $sql_startup);
    if( $row_startup = sqlsrv_fetch_array( $stmt_startup, SQLSRV_FETCH_ASSOC) ) {
        // should only be one row
        // HACK: not sure why numerics are being returned as strings but round() fixes it
        return array(
            'Station' => $row_startup['Member'],
            'Generated' => date_format($row_startup['Generated'], 'Y-m-d\TH:i:s').'.000Z',
            'lat' => floatval($row_startup['Latitude']),
            'lon' => floatval($row_startup['Longitude']),
            'DistanceFrom' => round($row_startup['DISTANCE_FROM']),
            'FFMC' => roundValue($row_startup['FFMC']),
            'DMC' => roundValue($row_startup['DMC']),
            'DC' => roundValue($row_startup['DC']),
            'APCP_0800' => roundValue($row_startup['APCP_0800']),
            'qry_Startup' => 'SELECT * FROM [INPUTS].[FCT_FWIObserved_By_Offset]('.($offset - 1).', '.$lat.', '.$long.', DEFAULT)'
        );
    }
    return array(
        'Station' => null,
        'Generated' => null,
        'lat' => null,
        'lon' => null,
        'DistanceFrom' => null,
        'FFMC' => 0,
        'DMC' => 0,
        'DC' => 0,
        'APCP_0800' => 0,
    );
}

function readModels($conn, $sql, $indices, &$dates_array)
{
    $stmt = try_query($conn,$sql);
    $modelsArray = array();
    $last_model = null;
    $last_member = null;
    $last_generated = null;
    $last_row = null;
    $last_key = null;
    $is_same = null;
    while( $row = sqlsrv_fetch_array( $stmt, SQLSRV_FETCH_ASSOC) ) {
        $cur_model = $row['Model'];
        $cur_member = $row['Member'];
        $temp = array();
        // output all the indices that we said we're going to provide
        foreach ($indices as $var) {
            array_push($temp, roundValue($row[$var]));
        }
        $is_same = $last_member == $cur_member && $last_model == $cur_model;
        // either new member or model
        if ($last_member != $cur_member || $last_model != $cur_model) {
            if (!is_null($last_row)) {
                $membersArray[$last_member] = $dataArray;
            }
            $dataArray = array();
            $last_member = $cur_member;
            
            // push all members into model array if new model
            if ($last_model != $cur_model) {
                if (!is_null($last_model)) {
                    $modelsArray[$last_model] = modelArray($last_row, $membersArray);
                }
                
                $membersArray = array();
                $last_model = $cur_model;
            }
        }
        $cur_date = date_format($row['ForTime'], 'Y-m-d\TH:i:s').'.000Z';
        // use a single array of dates and then the index in that array for the members
        if (!in_array($cur_date, $dates_array)) {
            array_push($dates_array, $cur_date);
        }
        $date_key = array_search($cur_date, $dates_array);
        if ($is_same && $last_key != ($date_key - 1))
        {
            // HACK: output is missing a day so just duplicate
            $dataArray[$date_key - 1] = $temp;
        }
        $last_key = $date_key;
        $dataArray[$date_key] = $temp;
        $last_row = $row;
    }
    if (!is_null($last_member)) {
        $membersArray[$last_member] = $dataArray;
    }
    if (!is_null($last_model)) {
        $modelsArray[$last_model] = modelArray($last_row, $membersArray);
    }
    return $modelsArray;
}

$WX_DATABASE = 'WX_'.date_format($startDate, 'Ym');

$conn = connect($WX_DATABASE);
# use dfoss database from startDate
$conn_dfoss = connect('DFOSS_'.date_format($startDate, 'Y'));
$conn_hindcast = connect('HINDCAST');
if ($conn && $conn_hindcast){
    // could probably look at only asking for what we're going to display
    $indices = array(
        'TMP',
        'RH',
        'WS',
        'WD',
        'APCP'
    );
    // if we've specified indices then only get those
    if (isset($_GET["indices"])) {
        $indices = explode(',', strval($_GET['indices']));
    }
    $outputArray = array();
    $outputArray['givenStart'] = $startDate->format('Y-m-d');
    $outputArray['FromDatabase'] = $WX_DATABASE;
    $outputArray['FakeDatabase'] = 'WX_'.date_format($startDate, 'Ym');
    // define which indices are going to be included and their order
    $outputArray['Indices'] = $indices;
    $outputArray['StartupValues'] = getStartup($conn_dfoss, $offset, $lat, $long);
    $dates_array = array();

    $sql = "SELECT *"
        //~ . " FROM [INPUTS].[FCT_Forecast](".$lat.", ".$long.", ".$numDays.")"
        . " FROM [INPUTS].[FCT_Forecast_By_Offset](".$offset.", ".$lat.", ".$long.", ".$numDays.")"
        . "  order by [Model], [Member], [ForTime]";
    $outputArray['qry_FCT_Forecast'] = $sql;
    $outputArray['Models'] = readModels($conn, $sql, $indices, $dates_array);
    // don't do anything with the hindcasts if not > 15 days because they're empty
    if ($numDays > 15) {
        $matches = array();
        $grades = array();
        $sql_match = "SELECT [Year], [AVG_VALUE], [GRADE]"
            . " FROM [HINDCAST].[FCT_HistoricMatch_By_Offset](".$offset.")"
            . " ORDER BY [GRADE] DESC";
        $outputArray['qry_FCT_HistoricMatch_By_Offset'] = $sql_match;
        $stmt = try_query($conn_hindcast,$sql_match);
        while( $row = sqlsrv_fetch_array( $stmt, SQLSRV_FETCH_ASSOC) ) {
            array_push($matches, $row['Year']);
            // only displays 2 decimal places but log scale so need more precision
            $grades[$row['Year']] = round($row['GRADE'], 4);
        }
        $outputArray['Matches'] = array('Order' => $matches, 'Grades' => $grades);
    }
    // NOTE: Needs to be included even if no historic matches since it's used for day 1 - 15 climate
    // NOTE: this automatically clips to 365 days in FCT_Hindcast
    // FIX: there's an issue with leap years not selecting Feb 29
    $sql = "SELECT *"
        . " FROM [HINDCAST].[FCT_Hindcast_By_Offset](".$offset.", ".$lat.", ".$long.", ".$numDays.")"
        . " order by [Model], [Member], [ForTime]";
    $outputArray['qry_FCT_Hindcast_By_Offset'] = $sql;
    $outputArray['Hindcast'] = readModels($conn_hindcast, $sql, $indices, $dates_array);
    
    $sql = "SELECT *"
        . " FROM [INPUTS].[FCT_Actuals](".$offset.", ".$numDays.", ".$lat.", ".$long.", DEFAULT)"
        . " order by [Model], [Member], [ForTime]";
    $outputArray['Actuals'] = readModels($conn_dfoss, $sql, $indices, $dates_array);
    
    $outputArray['ForDates'] = $dates_array;
    // we only need to know the day we started since they're sequential
    $outputArray['StartDate'] = $dates_array[0];
    echo json_encode($outputArray);
}
else{
    echo("Error could not connect to SQL database: ".print_r( sqlsrv_errors(), true));
}

/* Close the connection. */
sqlsrv_close( $conn);
sqlsrv_close( $conn_dfoss);
sqlsrv_close( $conn_hindcast);
?>