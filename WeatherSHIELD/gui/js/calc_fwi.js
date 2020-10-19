
// adapted from http://www.columbia.edu/~rf2426/index_files/FWI.vba
//'*******************************************************************************************
//'*
//'* Description: VBA module containing functions to calculate the components of
//'*              the Canadian Fire Weather Index system, as described in
//'*
//'*      Van Wagner, C.E. 1987. Development and structure of the Canadian Forest Fire
//'*      Weather Index System. Can. For. Serv., Ottawa, Ont. For. Tech. Rep. 35. 37 p.
//'*
//'*      Equation numbers from VW87 are listed throughout, to the right of the equations in
//'*      in the code.
//'*   
//'*      An more recent technical description can be found in:
//'*      http://www.cawcr.gov.au/publications/technicalreports/CTR_010.pdf
//'*
//'*      This module is essentially a direct C to VBA translation of Kerry Anderson's
//'*      fwi84.c code. The latitude adjustments were developed by Marty Alexander, and used
//'*      over Indonesia in the paper:
//'*
//'*      Field, R.D., Y. Wang, O. Roswintiarti, and Guswanto. A drought-based predictor of
//'*      recent haze events in western Indonesia. Atmospheric Environment, 38, 1869-1878, 2004.
//'* 
//'*      A technical description of the latitude adjustments can be found in Appendix 3 of:
//'*      http://cfs.nrcan.gc.ca/pubwarehouse/pdfs/29152.pdf
//'*
//'*      Robert Field, robert.field@utoronto.ca
//'*******************************************************************************************

//'*******************************************************************************************
//'* Function Name: FFMC
//'* Description: Calculates today's Fine Fuel Moisture Code
//'* Parameters:
//'*    TEMP is the 12:00 LST temperature in degrees celsius
//'*    RH is the 12:00 LST relative humidity in %
//'*    WIND is the 12:00 LST wind speed in kph
//'*    RAIN is the 24-hour acculumalted rainfall in mm, calculated at 12:00 LST
//'*    FFMCo is the previous day's FFMC
//'*******************************************************************************************
function calc_FFMC(TEMP, RH, WIND, RAIN, FFMCPrev) {
    //'''/* 1  '*/
    var Mo = 147.2 * (101.0 - FFMCPrev) / (59.5 + FFMCPrev);
    if (RAIN > 0.5)
    {
        //'''/* 2  '*/
        var rf = RAIN - 0.5;
        var Mr;
        if (Mo <= 150.0)
        {
            //'''/* 3a '*/
            Mr = Mo + 42.5 * rf * (Math.exp(-100.0 / (251.0 - Mo))) * (1 - Math.exp(-6.93 / rf));
        }
        else
        {
            //'''/* 3b '*/
            Mr = Mo + 42.5 * rf * (Math.exp(-100.0 / (251.0 - Mo))) * (1 - Math.exp(-6.93 / rf)) + 0.0015 * Math.pow((Mo - 150.0), 2) * Math.pow((rf), (0.5));
        }
        if (Mr > 250.0)
        {
           Mr = 250.0;
        }
        Mo = Mr;
    }
    //'''/* 4  '*/
    var m;
    var Ed = 0.942 * Math.pow((RH), (0.679)) + 11.0 * Math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - Math.exp(-0.115 * RH));
    if (Mo > Ed) {
        //'''/* 6a '*/
        var ko = 0.424 * (1.0 - Math.pow((RH / 100.0), 1.7)) + 0.0694 * Math.pow((WIND), (0.5)) * (1.0 - Math.pow((RH / 100.0), 8.0));
        //'''/* 6b '*/
        var kd = ko * 0.581 * Math.exp(0.0365 * TEMP);
        //'''/* 8  '*/
        m = Ed + (Mo - Ed) * Math.pow((10.0), (-kd));
    }
    else
    {
        //'''/* 5  '*/
        var Ew = 0.618 * Math.pow((RH), (0.753)) + 10.0 * Math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - Math.exp(-0.115 * RH));
        if (Mo < Ew)
        {
            //'''/* 7a '*/
            var kl = 0.424 * (1.0 - Math.pow(((100.0 - RH) / 100.0), 1.7)) + 0.0694 * Math.pow((WIND), 0.5) * (1 - Math.pow(((100.0 - RH) / 100.0), 8.0));
            //'''/* 7b '*/
            var kw = kl * 0.581 * Math.exp(0.0365 * TEMP);
            //'''/* 9  '*/
            m = Ew - (Ew - Mo) * Math.pow((10.0), (-kw));
        }
        else
        {
           m = Mo;
        }
    }
    //'''/* 10 '*/
    return 59.5 * (250.0 - m) / (147.2 + m);
}

//'*******************************************************************************************
//'* Function Name: DMC
//'* Description: Calculates today's Duff Moisture Code
//'* Parameters:
//'*    TEMP is the 12:00 LST temperature in degrees celsius
//'*    RH is the 12:00 LST relative humidity in %
//'*    RAIN is the 24-hour acculumalted rainfall in mm, calculated at 12:00 LST
//'*    DMCo is the previous day's DMC
//'*    Lat is the latitude in decimal degrees of the location for which calculations are being made
//'*    Month is the month of Year (1..12) for the current day's calculations.
//'*******************************************************************************************
function calc_DMC(TEMP, RH, RAIN, DMCPrev, MONTH, LAT) {
    var re, Mo, Mr, K, B, P, Pr, D1;
    if (RAIN > 1.5)
    {
        //'''/* 11  '*/
        re = 0.92 * RAIN - 1.27;
        //'''/* 12  '*/
        Mo = 20.0 + Math.exp(5.6348 - DMCPrev / 43.43);
        B;
        if (DMCPrev <= 33.0)
        {
            //'''/* 13a '*/
            B = 100.0 / (0.5 + 0.3 * DMCPrev);
        }
        else
        {
            if (DMCPrev <= 65.0)
            {
                //'''/* 13b '*/
                B = 14.0 - 1.3 * (Math.log(DMCPrev));
            }
            else
            {
                //'''/* 13c '*/
                B = 6.2 * Math.log(DMCPrev) - 17.2;
            }
        }
        //'''/* 14  '*/
        Mr = Mo + 1000.0 * re / (48.77 + B * re);
        //'''/* 15  '*/
        Pr = 244.72 - 43.43 * Math.log(Mr - 20.0);
        if (Pr > 0.0)
        {
           DMCPrev = Pr;
        }
        else
        {
           DMCPrev = 0.0;
        }
    }
    if (TEMP > -1.1)
    {
        Dl = DayLength(LAT, MONTH);
        K = 1.894 * (TEMP + 1.1) * (100.0 - RH) * Dl * 0.000001;
    }
    else
    {
        K = 0.0;
    }
    //'''/* 17  '*/
    return DMCPrev + 100.0 * K;
}

//'*******************************************************************************************
//'* Function Name: DC
//'* Description: Calculates today's Drought Code
//'* Parameters:
//'*    TEMP is the 12:00 LST temperature in degrees celsius
//'*    RAIN is the 24-hour acculumalted rainfall in mm, calculated at 12:00 LST
//'*    DCo is the previous day's DC
//'*    Lat is the latitude in decimal degrees of the location for which calculations are being made
//'*    Month is the month of Year (1..12) for the current day's calculations.
//'*******************************************************************************************
function calc_DC(TEMP, RAIN, DCPrev, MONTH, LAT) {
    if (RAIN > 2.8)
    {
        //'/* 18  */
        var rd = 0.83 * (RAIN) - 1.27;
        //'/* 19  */
        var Qo = 800.0 * Math.exp(-DCPrev / 400.0);
        //'/* 20  */
        var Qr = Qo + 3.937 * rd;
        //'/* 21  */
        var Dr = 400.0 * Math.log(800.0 / Qr);
        if (Dr > 0.0)
        {
           DCPrev = Dr;
        }
        else
        {
           DCPrev = 0.0;
        }
    }
    Lf = DayLengthFactor(LAT, MONTH - 1)
    var V;
    if (TEMP > -2.8)
    {
        //'/* 22  */
        V = 0.36 * (TEMP + 2.8) + Lf;
    }
    else
    {
        V = Lf;
    }
     
    if (V < 0.0)
    {
        V = 0.0;
    }
    //'/* 23  */
    var D = DCPrev + 0.5 * V;
    // HACK: don't allow negative values
    return Math.max(0.0, D)
}

//'*******************************************************************************************
//'* Function Name: ISI
//'* Description: Calculates today's Initial Spread Index
//'* Parameters:
//'*    WIND is the 12:00 LST wind speed in kph
//'*    FFMC is the current day's FFMC
//'*******************************************************************************************

function calc_ISI(WIND, FFMC) {
    //'''/* 24  '*/
    var fWIND = Math.exp(0.05039 * WIND);
    //'''/* 1   '*/
    var m = 147.2 * (101 - FFMC) / (59.5 + FFMC);
    //'''/* 25  '*/
    var fF = 91.9 * Math.exp(-0.1386 * m) * (1.0 + Math.pow((m), 5.31) / 49300000.0);
    //'''/* 26  '*/
    return 0.208 * fWIND * fF;
}

//'*******************************************************************************************
//'* Function Name: BUI
//'* Description: Calculates today's Buildup Index
//'* Parameters:
//'*    DMC is the current day's Duff Moisture Code
//'*    DC is the current day's Drought Code
//'*******************************************************************************************
function calc_BUI(DMC, DC) {
    var result;
    if (DMC <= 0.4 * DC)
    {
        // HACK: this isn't normally part of it but it's division by 0 without this
        if (0 == DC)
        {
            return 0;
        }
        //'''/* 27a '*/
        result = 0.8 * DMC * DC / (DMC + 0.4 * DC);
    }
    else
    {
        //'''/* 27b '*/
        result = DMC - (1.0 - 0.8 * DC / (DMC + 0.4 * DC)) * (0.92 + Math.pow((0.0114 * DMC), 1.7));
    }
    // HACK: don't allow negative values
    return Math.max(0.0, result);
}

//'*******************************************************************************************
//'* Function Name: FWI
//'* Description: Calculates today's Fire Weather Index
//'* Parameters:
//'*    ISI is current day's ISI
//'*    BUI is the current day's BUI
//'*******************************************************************************************

function calc_FWI(ISI, BUI) {
    var fD;
    if (BUI <= 80.0)
    {
        //'''/* 28a '*/
        fD = 0.626 * Math.pow((BUI), 0.809) + 2.0;
    }
    else
    {
        //'''/* 28b '*/
        fD = 1000.0 / (25.0 + 108.64 * Math.exp(-0.023 * BUI));
    }
    //'''/* 29  '*/
    var B = 0.1 * ISI * fD;
    if (B > 1.0)
    {
        //'''/* 30a '*/
        return Math.exp(2.72 * Math.pow((0.434 * Math.log(B)), 0.647));
    }
    else
    {
        //'''/* 30b '*/
        return B;
    }
}

//'*******************************************************************************************
//'* Function Name: DSR
//'* Description: Calculates today's Daily Severity Rating
//'* Parameters:
//'*    FWI is current day's FWI
//'*******************************************************************************************

function calc_DSR(FWI) {
    //'''/* 41 '*/
    return 0.0272 * Math.pow(FWI, 1.77);
}

//'* The following two functions refer to the MEA daylength adjustment 'note'.
// 
//'*******************************************************************************************
//'* Function Name: DayLengthFactor
//'* Description: Calculates latitude/date dependent day length factor for Drought Code
//'* Parameters:
//'*      Latitude is latitude in decimal degrees of calculation location
//'*      Month is integer (1..12) value of month of year for which calculation is being made
//'*
//'*******************************************************************************************

function DayLengthFactor(Latitude, MONTH) {
    var LfN = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6];
    var LfS = [6.4, 5.0, 2.4, 0.4, -1.6, -1.6, -1.6, -1.6, -1.6, 0.9, 3.8, 5.8];

    //'    '/* Use Northern hemisphere numbers */
    //'   '/* something goes wrong with >= */
    if (Latitude > 15.0)
    {
        return LfN[MONTH];
    }
    //'    '/* Use Equatorial numbers */
    else if (Latitude <= 15 >= Latitude > -15)
    {
        return 1.39;
    }
    //'    '/* Use Southern hemisphere numbers */
    else if (Latitude <= -15.0)
    {
        return LfS[MONTH];
    }
}

//'*******************************************************************************************
//'* Function Name: DayLength
//'* Description: Calculates latitude/date dependent day length for DMC calculation
//'* Parameters:
//'*      Latitude is latitude in decimal degrees of calculation location
//'*      Month is integer (1..12) value of month of year for which calculation is being made
//'*
//'*******************************************************************************************

function DayLength(Latitude, MONTH) {
    //'''/* Day Length Arrays for four diff't latitude ranges '*/
    var DayLength46N = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0];
    var DayLength20N = [7.9, 8.4, 8.9, 9.5, 9.9, 10.2, 10.1, 9.7, 9.1, 8.6, 8.1, 7.8];
    var DayLength20S = [10.1, 9.6, 9.1, 8.5, 8.1, 7.8, 7.9, 8.3, 8.9, 9.4, 9.9, 10.2];
    var DayLength40S = [11.5, 10.5, 9.2, 7.9, 6.8, 6.2, 6.5, 7.4, 8.7, 10.0, 11.2, 11.8];

    //''/* default to return error code '*/
    var retVal = null;
    
    //''/*
    //'    Use four ranges which respectively span:
    //'        - 90N to 33 N
    //'        - 33 N to 0
    //'        - 0 to -30
    //'        - -30 to -90
    //'*/
    if ((Latitude <= 90) && (Latitude > 33.0))
    {
        retVal = DayLength46N[MONTH - 1];
    }
    else if ((Latitude <= 33.0) && (Latitude > 15.0))
    {
        retVal = DayLength20N[MONTH - 1];
    }
    else if ((Latitude <= 15.0) && (Latitude > -15.0))
    {
        retVal = 9.0;
    }
    else if ((Latitude <= -15.0) && (Latitude > -30.0))
    {
        retVal = DayLength20S[MONTH - 1];
    }
    else if ((Latitude <= -30.0) && (Latitude >= -90.0))
    {
        retVal = DayLength40S[MONTH - 1];
    }
    return retVal
}

//'* Daylength utility functions


//'*******************************************************************************************
//'* Function Name: Date2Julian
//'* Description: Calculates Julian from calendar date
//'* Parameters: Month, Day and Year of date to convert
//'*
//'*******************************************************************************************

function Date2Julian(MONTH, Day, Year) {
    var DaysInMonth = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    var Julian = DaysInMonth[MONTH - 1] + Day;
    if ((Year % 4) == 0 && MONTH > 1)
    {
        Julian = Julian + 1;
    }
    return Julian;
}


//'''/*-------------------------------------------------------------------
//'   This subroutine was modified from a C program called sunrise.c
//'   written by Bear Giles (bear@fsl.noaa.gov) with algorithms for solar
//'   declination, equation of time, and length of day provided by
//'   Joseph Bartlo (jabartlo@delphi.com)
//'   -------------------------------------------------------------------'*/
function DayLengthExact(LAT, lng, jday) {
    if (LAT < -80.0 || LAT > 80.0 || lng < -180.0 || lng > 180.0)
    {
        return null;
    }
    else
    {
        //'''/* degrees to radians '*/
        var dtr = 3.1415926 / 180.0;

        //'''/* fraction of a year '*/
        var x = dtr * 360.0 / 366.0 * jday;

        //'''/* solar declination '*/
        var decl = dtr * (0.33029 - 22.9717 * Math.cos(x) + 3.8346 * Math.sin(x) - 0.3495 * Math.cos(2.0 * x) + 0.0261 * Math.sin(2.0 * x) - 0.1392 * Math.cos(3.0 * x) + 0.0727 * Math.sin(3.0 * x));

        //'''/* equation of time ? I don't recognize the significance of this '*/
        var eot = -0.0001062 + 0.009554 * Math.cos(x) - 0.122671 * Math.sin(x) - 0.05335 * Math.cos(2.0 * x) - 0.156121 * Math.sin(2.0 * x);
        var noon = 12.0 - (lng / 15.0) - eot;

        //'''/* ... so we'll just use Solar noon for now '*/
        var noon = 12.0;

        //'''/* fraction of a day in sunlight '*/
        var T = -Math.tan(dtr * (LAT)) * Math.tan(decl) + -Math.sin(dtr * 0.8) / (Math.cos(dtr * (LAT)) * Math.cos(decl)) ;
        if (T < -1.0 || T > 1.0)
        {
            return null;
        }
        else
        {
            return 2.0 * (12.0 / 3.1415926) * math.acos(T);
        }
    }
}
