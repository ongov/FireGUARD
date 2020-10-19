<?php
require 'connection.php';
?>
<!DOCTYPE html>
<!--
To change this license header, choose License Headers in Project Properties.
To change this template file, choose Tools | Templates
and open the template in the editor.
-->
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
            <title>WeatherSHIELD</title>
            <link rel="icon" href="favicon.png" type="image/vnd.microsoft.icon">
            
            <!-- Bootstrap -->
            <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
            <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
            <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
            <!--[if lt IE 9]>
              <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
              <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
            <![endif]-->
            
            <link rel="stylesheet" href="css/styles.css">
            
            <script type='text/javascript' src='js/utmconv.js'></script>
            <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
            <script type='text/javascript' src='js/jquery-1.11.3.min.js'></script>
            <!-- Include all compiled plugins (below), or include individual files as needed -->
            <script src="bootstrap/js/bootstrap.min.js"></script>
            <script src="js/jquery-ui.js"></script>
            <script type='text/javascript' src='js/jquery.validate.js'></script>
            <script type='text/javascript' src='js/DateCalculations.js'></script>
            <script>
                var wxValues = ['TMP', 'RH', 'APCP', 'WS', 'WD'];
                var fwiValues = ['FWI', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI'];
                var fbpValues = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
                                'D1', 'D2', 'S1', 'S2', 'S3',
                                'M125', 'M150', 'M175', 'M225', 'M250', 'M275',
                                'M330', 'M360', 'M3100', 'M430', 'M460', 'M4100',
                                'O1A25', 'O1A50', 'O1A75', 'O1A100', 'O1B25', 'O1B50', 'O1B75', 'O1B100'];
                var BOUNDS = {
                    'latitude': {'min': 41, 'max': 58},
                    'longitude': {'min': -96, 'max': -73}
                };
                var optionValues = {'fire': null, 'wxStn': null};
                
                function IsNumeric(n) {
                    return !isNaN(parseFloat(n)) && isFinite(n);
                }
                
                function setDateByNum(numDays){
                    if (undefined == numDays)
                    {
                        numDays = parseInt($('#numDays').val());
                        if (isNaN(numDays))
                        {
                            numDays = GetDays();
                        }
                    }
                    if (numDays <= 0)
                    {
                        numDays = 1;
                    }
                    $('#numDays').val(numDays)
                    if(IsNumeric(numDays)){
                        var newdate = $('#startDate').datepicker('getDate');
                        $('#endDate').datepicker('option', 'minDate', newdate);
                        newdate = new Date(newdate);
                        $('#dateOffset').val(dateDifference(getToday(), newdate));
                        newdate.setDate(newdate.getDate() + parseInt(numDays - 1));
                        $('#endDate').datepicker('setDate', newdate);
                    }
                    $('#endDate').blur();
                    $('#numDays').valid();
                }
                
                function GetDays() {
                    var theEnd = $('#endDate').datepicker('getDate');
                    var theStart = $('#startDate').datepicker('getDate');
                    return dateDifference(theStart, theEnd) + 1;
                }
                
                function getToday() {
                    // HACK: set to midnight by removing hours and minutes
                    var today = new Date();
                    today.setHours(0, 0, 0, 0);
                    return today;
                }
                
                function cal(whichDate){
                    var theEnd = $('#endDate').datepicker('getDate');
                    var theStart = $('#startDate').datepicker('getDate');
                    if ("Invalid Date" != theEnd && "Invalid Date" != theStart)
                    {
                        var numDays = dateDifference(theStart, theEnd) + 1;
                        setDateByNum(numDays);
                    }
                    else
                    {
                        setDateByNum();
                    }
                }
                
                //By default the end date will be Oct 31st but if we are looking
                //at a fire in late Oct we may wish to see beyond this date, so 
                //the default will be Oct 31st or minDefaultDays days from today
                function endDate(){
                    var curDate = $('#startDate').datepicker('getDate');
                    if (!curDate)
                    {
                        var date = new Date();
                        $('#startDate').datepicker('setDate', getToday());
                        var year = date.getFullYear();
                        var endofSeason = year + "-10-31";
                        $('#endDate').datepicker('setDate', new Date(endofSeason));
                        var minDefaultDays = 30;
                        var numDays = GetDays();
                        if(isNaN(numDays) || numDays < minDefaultDays){
                            numDays = minDefaultDays;
                        }
                        setDateByNum(minDefaultDays);
                    }
                    else
                    {
                        var numDays = GetDays();
                        $('#startDate').datepicker('setDate', curDate);
                        setDateByNum(minDefaultDays);
                    }
                }
                
                function changeLocation(id, locations) {
                    $('#' + id).blur();
                    var value = $('#' + id).val();
                    if ('' != value)
                    {
                        var loc = locations[value];
                        $('#txtLATDeg').val(loc[0]);
                        $('#txtLONGDeg').val(loc[1]);
                        changeLATLONGtoUTM(id);
                        $('#' + id).css('color', '#000000');
                    }
                    else {
                        $('#' + id).css('color', '#999999');
                    }
                }
                
                function changeSelect(elem) {
                    changeLocation(elem.id, optionValues[elem.id]);
                    $('#txtzone, #txtbasemap, #txtLATDeg, #txtLONGDeg').valid();
                }
                
                function fixLocation(id)
                {
                    if ('wxStn' != id) {
                        $('#wxStn').css('color', '#999999');
                        $('#wxStn').val(null);
                        $('#wxStnHidden').val(null);
                    }
                    if ('fire' != id) {
                        $('#fire').css('color', '#999999');
                        $('#fire').val(null);
                        $('#fireHidden').val(null);
                    }
                    if ('wxStn' == id) {
                        $('#wxStnHidden').val($('#wxStn').val());
                    }
                    if ('fire' == id) {
                        $('#fireHidden').val($('#fire').val());
                    }
                }
                
                function changeUTMtoLATLONG(id){
                    fixLocation(id);
                    var theZone = document.getElementById("txtzone").value;
                    var basemap = document.getElementById("txtbasemap").value;
                    if (0 >= theZone.length || 5 != basemap.length)
                    {
                        // zone and basemap not valid
                        return;
                    }
                    var block = 55;//document.getElementById("txtblock").value;
                    
                    if(IsNumeric(theZone) & IsNumeric(basemap) & IsNumeric(block)){
                        var easting = parseFloat(basemap.toString().substring(0,2)+block.toString().substring(0,1)+"000");
                        var northing = parseFloat(basemap.toString().substring(2,5)+block.toString().substring(1,2)+"000");
                        var zone = parseInt(theZone);
                        var southern = false;//parseFloat(document.getElementById("utmHemi").selectedIndex) == 1;

                        if (isNaN(easting) || isNaN(northing)) {
                            return;
                        }

                        if (isNaN(zone)) {
                            return;
                        }


                        if (northing < 0 || northing > 10000000) {
                            return;
                        }

                        utmconv.setDatum(1);
                        var latlon = utmconv.utmToLatLng(easting, northing, zone, southern);    // get lat/lon for this set of coordinates


                        //
                        // 0 is N or W hemisphere, 1 is S or E
                        //

                        setDecimalDegrees(latlon.lat, latlon.lng);           
                    }
                    else if(theZone==="" || basemap==="" )
                        return;
                    $('#txtzone, #txtbasemap, #txtLATDeg, #txtLONGDeg').valid();
                }
                
    
                function changeLATLONGtoUTM(id){
                    fixLocation(id);
                    var lat = document.getElementById("txtLATDeg").value;
                    var lon = document.getElementById("txtLONGDeg").value;
                    
                    if(IsNumeric(lat) & IsNumeric(lon)){
                        
                        lat = parseFloat(document.getElementById("txtLATDeg").value);
                        
                        lon = parseFloat(document.getElementById("txtLONGDeg").value);
                        
                        if (BOUNDS.latitude.min <= parseFloat(lat) && parseFloat(lat) <= BOUNDS.latitude.max){
                            if(BOUNDS.longitude.min <= parseFloat(lon) && parseFloat(lon)<= BOUNDS.longitude.max){
                                var mapDatum = 1;
                                utmconv.setDatum(mapDatum);
                                var coords = utmconv.latLngToUtm(lat, lon);
                                document.getElementById("txtLATDeg").value = parseFloat(document.getElementById("txtLATDeg").value).toFixed(5);
                                document.getElementById("txtLONGDeg").value = parseFloat(document.getElementById("txtLONGDeg").value).toFixed(5);
                                setUTM(coords.global.easting, coords.global.northing, coords.global.zone);//, coords.global.southern);
                            }
                        }
                    }
                    else if(lat==="" || lon==="" )
                        return;
                    $('#txtzone, #txtbasemap, #txtLATDeg, #txtLONGDeg').valid();
                }
                function setUTM(easting, northing, zone){
                    document.getElementById("txtzone").value=zone;
                    document.getElementById("txtbasemap").value=easting.toString().substring(0,2)+northing.toString().substring(0,3);
                }
                
                function setDecimalDegrees(lat,lon){
                    document.getElementById("txtLATDeg").value = lat.toFixed(5);
                    document.getElementById("txtLONGDeg").value = lon.toFixed(5);

                }
                
                function checkOptions(boolAllClicked, forWhat, values){
                    if (boolAllClicked) {
                        var checked = document.getElementById(forWhat).checked;
                        for (var v in values)
                        {
                            var elem = values[v];
                            document.getElementById(elem).checked = checked;
                        }
                    }
                    else {
                        var allChecked = true;
                        for (var v in values)
                        {
                            var elem = values[v];
                            allChecked = allChecked && document.getElementById(elem).checked;
                        }
                        document.getElementById(forWhat).checked = allChecked;
                    }
                }
            
            function setOverride()
            {
                var checked = document.getElementById("override").checked;
                $('#setFFMC').attr("disabled", !checked);
                $('#setDMC').attr("disabled", !checked);
                $('#setDC').attr("disabled", !checked);
                $('#setAPCP_0800').attr("disabled", !checked);
                $('#setFFMC').attr("required", checked);
                $('#setDMC').attr("required", checked);
                $('#setDC').attr("required", checked);
                $('#setAPCP_0800').attr("required", checked);
            }
            
            function loadAJAX(url, fct)
            {
                if (window.XMLHttpRequest) {
                    // code for IE7+, Firefox, Chrome, Opera, Safari
                    xmlhttp = new XMLHttpRequest();
                } else {
                    // code for IE6, IE5
                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                xmlhttp.open("GET", url, true);
                xmlhttp.send();
                xmlhttp.onreadystatechange = function () { fct(xmlhttp) };
            }
            
            function loadSelect(id, xmlhttp)
            {
                optionValues[id] = null;
                if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                    var elem = $('#' + id);
                    var placeholder = elem.attr('placeholder');
                    try
                    {
                        values = JSON.parse(xmlhttp.responseText);
                        for (var v in values)
                        {
                            var opt = $('<option>', { value: v, text: v });
                            opt.css('color', '#000000');
                            elem.append(opt);
                        }
                        $('#' + id + ' option[value=""]').text(placeholder);
                        optionValues[id] = values;
                        var hidValue = $('#' + id + 'Hidden').val();
                        if (hidValue)
                        {
                            elem.val(hidValue);
                        }
                    }
                    catch(e)
                    {
                        $('#' + id + ' option[value=""]').text("No " + placeholder + "s");
                        $('#' + id).attr("disabled", true);
                    }
                }
            }
            
            function loadValues(url, callback)
            {
                loadAJAX(url + "?minLat=" + BOUNDS.latitude.min + "&maxLat=" + BOUNDS.latitude.max +
                            "&minLon=" + BOUNDS.longitude.min + "&maxLon=" + BOUNDS.longitude.max,
                        callback);
            }
            
            function loadFires()
            {
                loadValues('getFires.php',
                        function(xmlhttp) {
                            loadSelect('fire', xmlhttp);
                        });
            }
            
            $(function () {
                loadValues('getStations.php',
                        function(xmlhttp) {
                            loadSelect('wxStn', xmlhttp);
                            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                                // HACK: load after weather stations so xmlhttp doesn't get overwritten
                                loadFires();
                            }
                        });
                setOverride();
            });
            </script>
            
    </head>
    <body>
        <div class="container form">
        <form id="formInputs" data-toggle="validator" role="form" style="margin-top: -25px;margin-bottom:-25px;" action="display.php" method="get">
            <center><img src="images\shieldwebsite.png" alt="WeatherSHIELD Logo" style="width:auto;height:75px;margin-bottom: 5px;"></center>
                <hr style="width: 75%">
                <h3>Forecast Location</h3>
                <center>
                <div class="container-fluid">
                    <div class='row-fluid'>
                        <div class="form-group col-xs-12 col-ms-6 col-sm-4">
                            UTM
                            <div class="form-group">
                                <label class="sr-only" for="txtzone">Zone</label>
                                <input class="input-small form-control" placeholder="Zone" type="text" name="txtzone" id="txtzone" maxlength="2" required>
                            </div>
                            <div class="form-group">
                                <label class="sr-only" for="txtbasemap">Basemap</label>
                                <input class="input-small form-control" placeholder="Basemap" type="text" name="txtbasemap" id="txtbasemap" maxlength="5" required>
                            </div>
                        </div>
                        <div class="form-group col-xs-12 col-ms-6 col-sm-4">
                            Decimal Degrees
                            <div class="form-group">
                                <label class="sr-only" for="txtLATDeg">Latitude</label>
                                <input class="input-small form-control" placeholder="Latitude" type="number" name="txtLATDeg" id="txtLATDeg" maxlength= "8" required>
                            </div>
                            <div class="form-group">
                                <label class="sr-only" for="txtLONGDeg">Longitude</label>
                                <input class="input-small form-control" placeholder="Longitude" type="number" name="txtLONGDeg" id="txtLONGDeg" maxlength= "10" required>
                            </div>
                        </div>
                        <div class="form-group col-xs-12 col-ms-6 col-sm-4">
                            Location
                            <div class="form-group">
                                <label class="sr-only" for="wxStn" style='text-align: vertical'>Weather Station</label>
                                <select style='color: #999999' class="input-small form-control" placeholder="Weather Station" id='wxStn' name='wxStn'>
                                    <option value='' style='color: #999999' disabled selected>Loading...</option>
                                </select>
                                <input type="hidden" disabled="disabled" class="hidden" name="wxStnHidden" id="wxStnHidden" />
                            </div>
                            <div class="form-group">
                                <label class="sr-only" for="fire">Fire</label>
                                <select style='color: #999999' class="input-small form-control" placeholder="Fire" id='fire' name='fire'>
                                    <option value='' style='color: #999999' disabled selected>Loading...</option>
                                </select>
                                <input type="hidden" disabled="disabled" class="hidden" name="fireHidden" id="fireHidden" />
                            </div>
                        </div>
                    </div>
                </div>
                </center>
                <hr>
                <h3>Date Range</h3>
                <div class="container-fluid">
                        <div class="col-xs-12 col-ms-4 col-sm-4 col-md-4 col-lg-4 form-group">
                            <label class="col-xs-4 col-ms-3 col-sm-3 control-label" for="startDate" style="margin-top: 7px">From</label>
                            <div class="col-xs-8 col-ms-9 col-sm-9">
                                <input style='width: 7em;' class="input-small form-control" placeholder="Start Date" type="text" id="startDate">
                            </div>
                        </div>
                        <div class="col-xs-12 col-ms-4 col-sm-4 col-md-4 col-lg-4 form-group">
                            <label class="col-xs-4 col-ms-3 col-sm-3 control-label" for="endDate" style="margin-top: 7px">To</label>
                            <div class="col-xs-8 col-ms-9 col-sm-9">
                                <input style='width: 7em;' class="input-small form-control" placeholder="End Date" type="text" id="endDate">
                            </div>
                        </div>
                        <div class="col-xs-12 col-ms-4 col-sm-4 col-md-4 col-lg-4 form-group">
                            <label class="col-xs-1 col-ms-1 col-sm-1 col-md-1 col-lg-1 control-label" for="numDays" style="margin-top: 7px">=</label>
                            <div class="col-xs-7 col-ms-7 col-sm-6">
                                <input type='hidden' id='dateOffset' name='dateOffset' />
                                <input style='width: 4em;' class="input-small form-control" placeholder="# Days" type="text" name="numDays" id="numDays" maxlength="4">
                            </div>
                            <label class="col-xs-4 col-ms-3 col-sm-3 control-label" for="numDays" style="margin-top: 7px">Days</label>
                        </div>
                </div>

            </center>
            <hr>
            <h3>Weather</h3>
            <div>
                <span class="inlineinput">
                    <input type="checkbox" name="weatherAll" id="weatherAll" checked="checked"></input>
                    <label for="weatherAll">All</label>
                    <input type="checkbox" name="TMP" id="TMP" checked="checked"></input>
                    <label for="TMP">Temperature</label>
                    <input type="checkbox" name="RH" id="RH" checked="checked"></input>
                    <label for="RH">Relative Humidity</label>
                    <input type="checkbox" name="WS" id="WS" checked="checked"></input>
                    <label for="WS">Wind Speed</label>
                    <input type="checkbox" name="WD" id="WD" checked="checked"></input>
                    <label for="WD">Wind Direction</label>
                    <input type="checkbox" name="APCP" id="APCP" checked="checked"></input>
                    <label for="APCP">Precipitation</label>
                </span>
            </div>
            <hr>
            <h3>CFFWI</h3>
            <div>
                <span class="inlineinput">
                    <input type="checkbox" name="IndiciesAll" id="IndiciesAll" checked="checked"></input>
                    <label for="IndiciesAll">All</label>
                    <input type="checkbox" name="FWI" id="FWI" checked="checked"></input>
                    <label for="FWI">FWI</label>
                    <input type="checkbox" name="FFMC" id="FFMC" checked="checked"></input>
                    <label for="FFMC">FFMC</label>
                    <input type="checkbox" name="DMC" id="DMC" checked="checked"></input>
                    <label for="DMC">DMC</label>
                    <input type="checkbox" name="DC" id="DC" checked="checked"></input>
                    <label for="DC">DC</label>
                    <input type="checkbox" name="ISI" id="ISI" checked="checked"></input>
                    <label for="ISI">ISI</label>
                    <input type="checkbox" name="BUI" id="BUI" checked="checked"></input>
                    <label for="BUI">BUI</label>
                    <input type="checkbox" name="override" id="override" onchange="setOverride()" />
                    <label for="override">Override Startup Indices</label>
                </span>
                <div class="container-fluid">
                    <div class="col-xs-7 col-ms-6 col-sm-3 col-md-3 col-lg-3 form-group">
                        <input class="input-small form-control" placeholder="FFMC" type="number" step="0.1" name="setFFMC" id="setFFMC" maxlength="4" disabled="disabled">
                    </div>
                    <div class="col-xs-7 col-ms-6 col-sm-3 col-md-3 col-lg-3 form-group">
                        <input class="input-small form-control" placeholder="DMC" type="number" step="0.1" name="setDMC" id="setDMC" maxlength="3" disabled="disabled">
                    </div>
                    <div class="col-xs-7 col-ms-6 col-sm-3 col-md-3 col-lg-3 form-group">
                        <input class="input-small form-control" placeholder="DC" type="number" step="0.1" name="setDC" id="setDC" maxlength="3" disabled="disabled">
                    </div>
                    <div class="col-xs-7 col-ms-6 col-sm-3 col-md-3 col-lg-3 form-group">
                        <input class="input-small form-control" placeholder="0800 Precip." type="number" step="0.1" name="setAPCP_0800" id="setAPCP_0800" maxlength="3" disabled="disabled">
                    </div>
                </div>
            </div>
            <hr>
            <h3>Rate of Spread</h3>
            <div>
                <span class="inlineinput">
                    <input type="checkbox" name="fbpAll" id="fbpAll" checked="checked"></input>
                    <label for="fbpAll">All</label>
                    <br />
                    <div style='margin-left: 30px;display: inline-block;'>
                        <input type="checkbox" name="C1" id="C1" checked="checked"></input>
                        <label for="C1">C-1</label>
                        <input type="checkbox" name="C2" id="C2" checked="checked"></input>
                        <label for="C2">C-2</label>
                        <input type="checkbox" name="C3" id="C3" checked="checked"></input>
                        <label for="C3">C-3</label>
                        <input type="checkbox" name="C4" id="C4" checked="checked"></input>
                        <label for="C4">C-4</label>
                        <input type="checkbox" name="C5" id="C5" checked="checked"></input>
                        <label for="C5">C-5</label>
                        <input type="checkbox" name="C6" id="C6" checked="checked"></input>
                        <label for="C6">C-6</label>
                        <input type="checkbox" name="C7" id="C7" checked="checked"></input>
                        <label for="C7">C-7</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>
                        <input type="checkbox" name="D1" id="D1" checked="checked"></input>
                        <label for="D1">D-1</label>
                        <input type="checkbox" name="D2" id="D2" checked="checked"></input>
                        <label for="D2">D-2</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>
                        <input type="checkbox" name="S1" id="S1" checked="checked"></input>
                        <label for="S1">S-1</label>
                        <input type="checkbox" name="S2" id="S2" checked="checked"></input>
                        <label for="S2">S-2</label>
                        <input type="checkbox" name="S3" id="S3" checked="checked"></input>
                        <label for="S3">S-3</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>M-1
                        <input type="checkbox" name="M125" id="M125" checked="checked"></input>
                        <label for="M125">25%</label>
                        <input type="checkbox" name="M150" id="M150" checked="checked"></input>
                        <label for="M150">50%</label>
                        <input type="checkbox" name="M175" id="M175" checked="checked"></input>
                        <label for="M175">75%</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>M-2
                        <input type="checkbox" name="M225" id="M225" checked="checked"></input>
                        <label for="M225">25%</label>
                        <input type="checkbox" name="M250" id="M250" checked="checked"></input>
                        <label for="M250">50%</label>
                        <input type="checkbox" name="M275" id="M275" checked="checked"></input>
                        <label for="M275">75%</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>M-3
                        <input type="checkbox" name="M330" id="M330" checked="checked"></input>
                        <label for="M330">30%</label>
                        <input type="checkbox" name="M360" id="M360" checked="checked"></input>
                        <label for="M360">60%</label>
                        <input type="checkbox" name="M3100" id="M3100" checked="checked"></input>
                        <label for="M3100">100%</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>M-4
                        <input type="checkbox" name="M430" id="M430" checked="checked"></input>
                        <label for="M430">30%</label>
                        <input type="checkbox" name="M460" id="M460" checked="checked"></input>
                        <label for="M460">60%</label>
                        <input type="checkbox" name="M4100" id="M4100" checked="checked"></input>
                        <label for="M4100">100%</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>O-1a
                        <input type="checkbox" name="O1A25" id="O1A25" checked="checked"></input>
                        <label for="O1A25">25%</label>
                        <input type="checkbox" name="O1A50" id="O1A50" checked="checked"></input>
                        <label for="O1A50">50%</label>
                        <input type="checkbox" name="O1A75" id="O1A75" checked="checked"></input>
                        <label for="O1A75">75%</label>
                        <input type="checkbox" name="O1A100" id="O1A100" checked="checked"></input>
                        <label for="O1A100">100%</label>
                    </div>
                    <div style='margin-left: 30px;display: inline-block;'>O-1b
                        <input type="checkbox" name="O1B25" id="O1B25" checked="checked"></input>
                        <label for="O1B25">25%</label>
                        <input type="checkbox" name="O1B50" id="O1B50" checked="checked"></input>
                        <label for="O1B50">50%</label>
                        <input type="checkbox" name="O1B75" id="O1B75" checked="checked"></input>
                        <label for="O1B75">75%</label>
                        <input type="checkbox" name="O1B100" id="O1B100" checked="checked"></input>
                        <label for="O1B100">100%</label>
                    </div>
                </span>
            </div>
            <hr>
            <h3>Analysis</h3>
            <div>
                <span class="inlineinput">
                    <input type="checkbox" name="Scenarios" id="Scenarios" />
                    <label for="Scenarios">Scenarios</label>
                </span>
            </div>
            <hr style="width: 75%">
            <div style="margin-top: 15px" align="center">
                <input type="submit" value="Submit" class="button button-block">
            </div>
            <br />
            <center style="margin-top: -5px;margin-bottom: 0px;"><a href='https://www.mdpi.com/2571-6255/3/2/16' style="font-weight: bold; color: #AAAAFF;">Info/About</a></center>
        </form>
        </div>
        <?php require 'footer.php' ?>
        <script>
            function setupOptions(forWhat, values)
            {
                $('#' + forWhat).change(function (){ checkOptions(true, forWhat, values); });
                var all = values.map(function (x) { return '#' + x; }).join(', ');
                $(all).change(function (){ checkOptions(false, forWhat, values); });
            }
            
            $(document).ready(function () {
                $('#txtzone, #txtbasemap').change(function (){ changeUTMtoLATLONG(); });
                $('#txtLATDeg, #txtLONGDeg').change(function (){ changeLATLONGtoUTM(); });
                $('#wxStn, #fire').change(function (){ changeSelect(this); });
                $('#numDays').change(function (){ setDateByNum(); });
                $('#startDate').change(function (){ cal('startDate'); });
                $('#endDate').change(function (){ cal('endDate'); });
                setupOptions('weatherAll', wxValues);
                setupOptions('IndiciesAll', fwiValues);
                setupOptions('fbpAll', fbpValues);
                $('#formInputs').validate({
                    rules: {
                        txtLATDeg: {
                            required: true,
                            max: BOUNDS.latitude.max,
                            min : BOUNDS.latitude.min
                        },
                        txtLONGDeg: {
                            required: true,
                            max : BOUNDS.longitude.max,
                            min : BOUNDS.longitude.min
                        },
                        txtzone: {
                            required: true,
                            max: utmconv.latLngToUtm(BOUNDS.latitude.max, BOUNDS.longitude.max).global.zone,
                            min: utmconv.latLngToUtm(BOUNDS.latitude.max, BOUNDS.longitude.min).global.zone
                        },
                        txtbasemap: {
                            required: true,
                            maxlength: 5,
                            minlength: 5,
                        },
                        numDays: {
                            required: true,
                            min: 1
                        },
                        setFFMC: {
                            max: 101,
                            min: 0
                        },
                        setDMC: {
                            min: 0
                        },
                        setDC: {
                            min: 0
                        },
                        setAPCP_0800: {
                            min: 0
                        }
                    }
                });
                $('#startDate').datepicker({
                    dateFormat: 'yy-mm-dd',
                    maxDate: 0,
                });
                $('#endDate').datepicker({
                    dateFormat: 'yy-mm-dd',
                    minDate: 0 
                });
                endDate();
            });
        </script>
    </body>
</html>
