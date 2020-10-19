<html>
    <title>WeatherSHIELD Usage</title>
    <link rel="stylesheet" href="css/styles.css">

    <head>
        <script type='text/javascript' src='js/jquery-1.11.3.min.js'></script>
        <script type="text/javascript" src="js/jspdf.js"></script>
        <script type="text/javascript" src="js/canvg.js"></script>
        <script type="text/javascript" src="js/rgbcolor.js"></script>
        <script src="js/DateCalculations.js"> </script>
        <script src="js/calc_fwi.js"></script>
        <script src="js/weatherSHIELD_1.js"> </script>
        
        <script type='text/javascript'>
        $(function () {
            document.getElementById("msg").innerHTML = "Please wait while data loads.";
            if (window.XMLHttpRequest) {
                // code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp = new XMLHttpRequest();
            } else {
                // code for IE6, IE5
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }
            
            xmlhttp.open("GET","getUsage.php",true);
            xmlhttp.send();
            xmlhttp.onreadystatechange = function() {
                if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                    try{
                        multiArray = JSON.parse(xmlhttp.responseText);
                        // convert date strings into actual dates right away
                        var tableBody = $('#tblUsage');
                        for (var r in multiArray) {
                          var row = multiArray[r];
                          //~ row['Timeof'] = new Date(row['Timeof']);
                          var tr = $('<tr>').appendTo(tableBody);
                          for (var c in row) {
                            var col = row[c];
                            tr.append('<td>' + col + '</td>');
                          }
                        }
                        document.getElementById("msg").innerHTML = "";
                        
                        
                    }
                    catch(e){
                        multiArray = xmlhttp.responseText;                        
                        document.getElementById("msg").innerHTML = "Error:" + e + " " +multiArray;
                        //Put in fake data upon error?
                        multiArray= [];
                    }
                    
                    }

                }
        });
    
        </script>
    </head>
    <body>
    
    <!--<img src="..\images\blah.png" style="width:304px;height:auto;" alt="big logo">
    <img src="..\images\bars.png" alt="Green Bars">-->
    <div align='center'>
        <table id='tblUsage'>
          <tr>
            <th>IP</th>
            <th>Time</th>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Offset</th>
            <th># Days</th>
            <th>Query</th>
          </tr>
        </table>
    <p id='msg'></p>
    </div>

</html>
