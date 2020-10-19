<?php
$lat = floatval($_GET['txtLATDeg']);
$long = floatval($_GET['txtLONGDeg']);
$offset = intval($_GET['dateOffset']);
$numDays = intval(test_input($_GET["numDays"]));
$show_scenarios = isset($_GET["Scenarios"]) ? 'true' : 'false';
$override = isset($_GET["override"]) ? 'true' : 'false';
$MAX_GRADE = isset($_GET["maxGrade"]) ? floatval($_GET['maxGrade']) : 2.1;

$query = $_SERVER['QUERY_STRING'];

//define variables and set them to false or empty
$strZone = "";
$strBasemap = "";
$strLat = "";
$strLong = "";
date_default_timezone_set('America/New_York');
$reportDate = date("Y-m-d Hi");
// NOTE: assuming that boolean values are only set if they are true
// set these to value of 'all' fields so that if we add indices later then
// url will turn them on
$APCP = $TMP = $RH = $WS = $WD = isset($_GET["weatherAll"]);
$FWI = $FFMC = $DMC = $DC = $ISI = $BUI = isset($_GET["IndiciesAll"]);
$show_indices = array();
if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $fire = test_input($_GET["fire"]);
    $wxstn = test_input($_GET["wxStn"]);
    $strZone = test_input($_GET["txtzone"]);
    $strBasemap = test_input($_GET["txtbasemap"]);            
    $strLat = test_input($_GET["txtLATDeg"]);
    $strLong= test_input($_GET["txtLONGDeg"]);
    $strLatLong = $strLat. ' x ' .$strLong;
    $timezone = new DateTimeZone('UTC');
    $cur_date = new DateTime('midnight', $timezone);
    $cur_date->modify($offset.' days');
    $cur_date->modify('+18 hours');
    $startDate = $cur_date->format('Y-m-d');
    //Because we are counting today as a day we need to minus one to 
    //make the total range correct
    $tempNum = $numDays - 1;
    $cur_date->modify($tempNum. " days");
    $endDate = $cur_date->format('Y-m-d');
    // set $show_indices keys based on what indices are needed to calculate values
    if ($APCP || isset($_GET["APCP"])) { $show_indices['APCP'] = true; };
    if ($TMP || isset($_GET["TMP"])) { $show_indices['TMP'] = true; };
    if ($RH || isset($_GET["RH"])) { $show_indices['RH'] = true; };
    if ($WS || isset($_GET["WS"])) { $show_indices['WS'] = true; };
    if ($WD || isset($_GET["WD"])) { $show_indices['WD'] = true; };
    // NOTE: javascript expects that these indices will appear in this order when they appear
    if ($FFMC || isset($_GET["FFMC"])) { $show_indices['FFMC'] = true; };
    if ($DMC || isset($_GET["DMC"])) { $show_indices['DMC'] = true; };
    if ($DC || isset($_GET["DC"])) { $show_indices['DC'] = true; };
    if ($ISI || isset($_GET["ISI"])) { $show_indices['ISI'] = true; };
    if ($BUI || isset($_GET["BUI"])) { $show_indices['BUI'] = true; };
    if ($FWI || isset($_GET["FWI"])) { $show_indices['FWI'] = true; };
}

function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

function makeJSArray($arr) {
return '['.implode(', ', array_map(create_function('$v', 'return "\'".$v."\'";'), array_keys($arr))).']';
}
?>
<script type='text/javascript' src='js/utmconv.js'></script>
<script type='text/javascript'>
        var MAX_GRADE = <?php echo $MAX_GRADE ?>;
        var strLatLong = "<?php echo $strLatLong ?>";
        var DATE_OFFSET = <?php echo $offset ?>;
        var strStartDate= "<?php echo $startDate ?>";
        var strEndDate = "<?php echo $endDate ?>";
        var NUM_DAYS = "<?php echo $numDays ?>";
        var strReportDate = "<?php echo $reportDate ?>";
        var LATITUDE = <?php echo $strLat ?>;
        var LONGITUDE = <?php echo $strLong ?>;  
        var mapDatum = 1;
        utmconv.setDatum(mapDatum);
        var coords = utmconv.latLngToUtm(LATITUDE, LONGITUDE);
        var strZone = coords.global.zone.toString();
        var strBaseMap = coords.global.easting.toString().substring(0,2)+coords.global.northing.toString().substring(0,3);
        var SHOW_INDICES = <?php echo makeJSArray($show_indices) ?>;
        var SHOW_SCENARIOS = <?php echo $show_scenarios ?>;
        var OVERRIDE_FWI = <?php echo $override ?>;
        var MANUAL_STARTUP = {
            'FFMC': <?php echo (isset($_GET["setFFMC"]) ? floatval($_GET['setFFMC']) : 'null') ?>,
            'DMC': <?php echo (isset($_GET["setDMC"]) ? floatval($_GET['setDMC']) : 'null') ?>,
            'DC': <?php echo (isset($_GET["setDC"]) ? floatval($_GET['setDC']) : 'null') ?>,
            'APCP_0800': <?php echo (isset($_GET["setAPCP_0800"]) ? floatval($_GET['setAPCP_0800']) : 'null') ?>
        };
</script>
