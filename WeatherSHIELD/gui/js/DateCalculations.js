function timezoneString()
{
    var offset = new Date().getTimezoneOffset();
    var hours = offset / 60;
    var minutes = (offset % 60);
    return 'T' + ('0' + hours).slice(-2) + ':' + ('0' + minutes).slice(-2) + ':00'
}

function formatDate(d) {
    var dd = d.getDate();
    var mm = d.getMonth()+1;
    var y = d.getFullYear();
                    
    if (mm < 10) mm = "0" + mm;
    if (dd < 10) dd = "0" + dd;
    return y + "-" + mm + '-' + dd;
}

function toDate(str)
{
    return new Date(str + timezoneString());
}

/*
 * Take the date array and return it in the format that will make it 
 * a bit cleaner to read
 * 
 */
function shortDate(theDate, with_day) {
    var with_day = (undefined != with_day) && with_day;
    var month_names_short= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var day_names_short = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var dd = theDate.getDate();
    var mm = theDate.getMonth();
    
    return (with_day ? (day_names_short[theDate.getDay()] + '<br />') : '') + month_names_short[mm] + ' ' + dd;
}


function dateDifference(startDate, endDate) {
    return Math.round((endDate - startDate) / (1000 * 60 * 60 * 24));
}


function compareDates(startDate, endDate)
{
    var a = new Date(startDate);
    var b = new Date(endDate);
    a.setUTCHours(0, 0, 0, 0);
    b.setUTCHours(0, 0, 0, 0);
    //~ return (a < b) ? -1 : ((a > b) ? 1 : 0);
    return (a > b) - (a < b);
}
