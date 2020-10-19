
function ToRadians(x)
{
    return x / 180.0 * Math.PI;
}

function ToDegrees(x)
{
    return x * 180.0 / Math.PI;
}


var Inputs = function()
{
    var self = this;
    var ffmc;
    var ws;
    var gfl;
    var bui;
    var foliar_moisture;
    var time;
    var pattern;
    var mon;
    var waz;
    var ps;
    var saz;
    var cur;
    var elev;
    var hour;
    var hourly;
};

var FireStruc = function()
{
    var self = this;
    var ros;
    var dist;
    var rost;
    var cfb;
    var fc;
    var cfc;
    var time;
    var rss;
    var isi;
    var fd;
    var fi;
};

var MainOuts = function()
{
    var self = this;
    var hffmc;
    var sfc;
    var csi;
    var rso;
    var fmc;
    var sfi;
    var rss;
    var isi;
    var be;
    var sf;
    var raz;
    var wsv;
    var ff;
    var covertype;
};

var SndOuts = function()
{
    var self = this;
    var lb;
    var area;
    var perm;
    var pgr;
    var lbt;
};


var test_input = new Inputs();


var slopelimit_isi = 0.01;

var FuelType = function(cover, fueltype, a, b, c, q, bui0, cbh, cfl, isOpen)
{
    function open_acceleration(cfb)
    {
        return 0.115;
    }
    
    function closed_acceleration(cfb)
    {
        return 0.115 - 18.8 * Math.pow(cfb, 2.5) * Math.exp(-8.0*cfb);
    }

    var self = this;
    self.cover = cover;
    self.fueltype = fueltype;
    self.q = q;
    self.bui0 = bui0;
    self.cbh = cbh;
    self.cfl = cfl;
    self.a = a;
    self.b = b;
    self.c = c;
    self.canopy = (isOpen) ? 'o' : 'c';
    if (self.isOpen)
    {
        self.acceleration = open_acceleration;
    }
    else
    {
        self.acceleration = closed_acceleration;
    }
    
    //~ public abstract double ros_calc(Inputs inp, double isi);
    //~ public abstract double isf_calc(Inputs inp, MainOuts at, double isi);
    //~ public abstract double surf_fuel_consump(Inputs inp);
    
    //~ protected delegate double accel_delegate(double cfb);
    //~ protected accel_delegate acceleration;
    

    self.crown_consump = function (cfb)
    {
        return self.cfl * cfb;
    };
    

    self.ros_basic = function (isi)
    {
        return (a * Math.pow((1.0 - Math.exp(-1.0 * b * isi)), c));
    };

    self.calculate = function (data, at, sec, hptr, fptr, bptr)
    {
        zero_main(at);
        zero_sec(sec);
        zero_fire(hptr);
        zero_fire(fptr);
        zero_fire(bptr);
        at.covertype = cover;
        //fuel_coefs c = Fuels[data.fueltype];
        at.ff = self.ffmc_effect(data.ffmc);
        at.rss = self.rate_of_spread(data, at);
        hptr.rss = at.rss;
        at.sfc = self.surf_fuel_consump(data);
        at.sfi = self.fire_intensity(at.sfc, at.rss);


        if (self.cover == 'c')
        {
            at.fmc = data.foliar_moisture;
            at.csi = self.crit_surf_intensity(at.fmc);
            at.rso = self.critical_ros(at.sfc, at.csi);
        }
        self.p_fire_behaviour(at, hptr);
        
        sec.lb = self.l_to_b(at.wsv);
        bptr.isi = self.backfire_isi(at);
        bptr.rss = self.backfire_ros(data, at, bptr.isi);
        
        self.p_fire_behaviour(at, bptr);

        fptr.ros = self.flankfire_ros(hptr.ros, bptr.ros, sec.lb);
    };
    
    self.calculate_full = function (data, at, sec, hptr, fptr, bptr)
    {
        self.calculate(data, at, sec, hptr, fptr, bptr);

        hptr.fi = self.s_fire_behaviour(at, hptr);
        //HACK: set this since final_ros() in fire_behaviour() should have set it
        at.rss = hptr.rss;

        bptr.fi = self.s_fire_behaviour(at, bptr);

        fptr.rss = self.flankfire_ros(hptr.rss, bptr.rss, sec.lb);
        fptr.fi = self.flank_fire_behaviour(at, fptr);
        
        self.fire_dist(data, at, hptr);
        self.fire_dist(data, at, bptr);
        if (data.pattern == 1 && data.time > 0)
        {
            var accn = self.acceleration(hptr.cfb);
            fptr.dist = self.flank_spread_distance(data, fptr, sec, hptr.rost, bptr.rost, hptr.dist, bptr.dist, sec.lb, accn);
            fptr.time = self.time_to_crown(fptr.ros, at.rso, accn);
        }
        else
        {
            self.set_all(fptr, data.time);
        }

        sec.area = self.area((hptr.dist + bptr.dist), fptr.dist);
        if (data.pattern == 1 && data.time > 0)
            sec.perm = self.perimeter(hptr, bptr, sec, sec.lbt);
        else
            sec.perm = self.perimeter(hptr, bptr, sec, sec.lb);
    };
    
    self.fire_dist = function (data, at, f)
    {
        if (data.pattern == 1 && data.time > 0)
        {
            var accn = self.acceleration(f.cfb);
            f.dist = self.spread_distance(data, f, accn);
            f.time = self.time_to_crown(f.ros, at.rso, accn);
        }
        else
        {
            self.set_all(f, data.time);
        }
    };
    
    self.ffmc_effect = function (ffmc)
    {
        var mc = 147.2 * (101.0 - ffmc) / (59.5 + ffmc);
        return 91.9 * Math.exp(-0.1386 * mc) * (1 + Math.pow(mc, 5.31) / 49300000.0);
    }
    
    self.p_fire_behaviour = function (at, f)
    {
        var sfi = self.fire_intensity(at.sfc, f.rss);
        if (self.is_crown(at.csi, sfi) && self.cover != 'n')
        {
            f.cfb = self.crown_frac_burn(f.rss, at.rso);
            f.fd = self.fire_description(f.cfb);
            f.ros = self.final_ros(at.fmc, f.isi, f.cfb, f.rss);
            f.cfc = self.crown_consump(f.cfb);
            f.fc = f.cfc + at.sfc;
        }
        else
        {
            f.fc = at.sfc;
            f.cfb = 0.0;
            f.fd = 'S';
            f.ros = f.rss;
        }
    };

    self.s_fire_behaviour = function (at, f)
    {
        var sfi = self.fire_intensity(at.sfc, f.rss);
        return (self.is_crown(at.csi, sfi) && self.cover != 'n') ?
            self.fire_intensity(f.fc, f.ros) : sfi;
    };

    self.flank_fire_behaviour = function (at, f)
    {
        var sfi = self.fire_intensity(at.sfc, f.rss);
        var fi;
        if (self.is_crown(at.csi, sfi) && self.cover != 'n')
        {
            f.cfb = self.crown_frac_burn(f.rss, at.rso);
            f.fd = self.fire_description(f.cfb);
            f.cfc = self.crown_consump(f.cfb);
            f.fc = f.cfc + at.sfc;
            fi = self.fire_intensity(f.fc, f.ros);
        }
        else
        {
            f.fc = at.sfc;
            fi = sfi;
            f.cfb = 0.0;
            f.fd = 'S';
            /*   f->ros=f->rss;  removed...v4.5   should not have been here ros set in flankfire_ros()  */
        }
        return (fi);
    };

    self.rate_of_spread = function (inp, at)
    {
        at.ff = self.ffmc_effect(inp.ffmc);
        at.raz = inp.waz;
        var isz = 0.208 * at.ff;
        at.wsv = (inp.ps > 0) ? self.slope_effect(inp, at, isz) : inp.ws;
        var fw = (at.wsv < 40.0) ? Math.exp(0.05039 * at.wsv) : (12.0 * (1.0 - Math.exp(-0.0818 * (at.wsv - 28))));
        at.isi = isz * fw;
        var rsi = self.ros_calc(inp, at.isi);
        at.rss = rsi * self.bui_effect(at, inp.bui);
        return (at.rss);
    };
    
    self.slope_effect = function (inp, at, isi)
    {
        var wse;
        var ps = inp.ps * 1.0;
        if (ps > 60.0)
            ps = 60.0;
        at.sf = Math.exp(3.533 * Math.pow(ps / 100.0, 1.2));

        var isf = self.isf_calc(inp, at, isi);

        if (isf == 0.0)
        {
            // should this be 0.0001 really
            isf = isi;
        } 
        var wse1 = Math.log(isf / (0.208 * at.ff)) / 0.05039;
        if (wse1 <= 40.0)
            wse = wse1;
        else
        {
            var max_isf = 0.999 * 2.496 * at.ff;
            if (isf > max_isf)
                isf = max_isf;
            wse = 28.0 - Math.log(1.0 - isf / (2.496 * at.ff)) / 0.0818;
        }
        var wsx = inp.ws * Math.Sin(inp.waz);
        var wsy = inp.ws * Math.Cos(inp.waz);
        var wsex = wse * Math.Sin(inp.saz);
        var wsey = wse * Math.Cos(inp.saz);
        var wsvx = wsx + wsex;
        var wsvy = wsy + wsey;
        var wsv = Math.Sqrt(wsvx * wsvx + wsvy * wsvy);
        var raz = ToDegrees(Math.Acos(wsvy / wsv));
        if (wsvx < 0)
            raz = 360 - raz;
        at.raz = ToRadians(raz);
        //at.r_az = Math.Acos(wsvy / wsv);
        //if (wsvx < 0)
        //    at.r_az = 2 * Math.PI - at.r_az;

        return wsv;
    };

    self.l_to_b = function (ws)
    {
        return (1.0 + 8.729 * Math.pow(1.0 - Math.exp(-0.030 * ws), 2.155));
    };


    self.bui_effect = function (at, bui)
    {
        var bui_avg = 50.0;

        if (bui == 0)
            bui = 1.0;
        at.be = Math.exp(bui_avg * Math.log(q) * ((1.0 / bui) - (1.0 / bui0)));
        return (at.be);
    };

    self.fire_intensity = function (fc, ros)
    {
        return (300.0 * fc * ros);
    };

    self.limit_isf = function (mu, rsf)
    {
        var check = (rsf > 0.0) ? (1.0 - Math.pow((rsf / (mu * a)), (1.0 / c))) : 1.0;
        if (check < slopelimit_isi)
            check = slopelimit_isi;

        return (1.0 / (-1.0 * b)) * Math.log(check);
    };

    self.crit_surf_intensity = function (fmc)
    {

        return (0.001 * Math.pow(self.cbh * (460.0 + 25.9 * fmc), 1.5));
    };

    self.critical_ros = function (sfc, csi)
    {
        return (sfc > 0) ? (csi / (300.0 * sfc)) : (0.0);
    }

    self.crown_frac_burn = function (rss, rso)
    {
        var cfb = 1.0 - Math.exp(-0.230 * (rss - rso));
        return (cfb > 0 ? cfb : 0.0);
    }

    self.is_crown = function (csi, sfi)
    {
        return (sfi > csi);
    }

    self.fire_description = function (cfb)
    {
        if (cfb < 0.1)
            return ('S');
        if (cfb < 0.9 && cfb >= 0.1)
            return ('I');
        if (cfb >= 0.9)
            return ('C');
        return ('*');
    }

    self.final_ros = function (fmc, isi, cfb, rss)
    {
        return (rss);
    }

    self.foliar_mois_effect = function (isi, fmc)
    {
        var fme_avg = 0.778;
        var fme = 1000.0 * Math.pow(1.5 - 0.00275 * fmc, 4.0) / (460.0 + 25.9 * fmc);
        var rsc = 60.0 * (1.0 - Math.exp(-0.0497 * isi)) * fme / fme_avg;
        return (rsc);
    }

    self.set_all = function (ptr, time)
    {
        ptr.time = 0;
        ptr.rost = ptr.ros;
        ptr.dist = time * ptr.ros;
    }
    
    self.backfire_isi = function (at)
    {
        var bfw = Math.exp(-0.05039 * at.wsv);
        return (0.208 * at.ff * bfw);
    }

    self.backfire_ros = function (inp, at, bisi)
    {
        var bros = self.ros_calc(inp, bisi);
        bros *= self.bui_effect(at, inp.bui);
        return (bros);
    }

    self.area = function (dt, df)
    {
        var a = dt / 2.0;
        var b = df;
        return (a * b * Math.PI / 10000.0);
    }

    self.perimeter = function (h, b, sec, lb)
    {
        var mult = (Math.PI * (1.0 + 1.0 / lb) * (1.0 + Math.pow(((lb - 1.0) / (2.0 * (lb + 1.0))), 2.0)));
        var p = (h.dist + b.dist) / 2.0 * mult;
        sec.pgr = (h.ros + b.ros) / 2.0 * mult;

        return (p);
    }

    self.flankfire_ros = function (ros, bros, lb)
    {
        return ((ros + bros) / (lb * 2.0));
    }

    self.flank_spread_distance = function (inp, ptr, sec, hrost, brost, hd, bd, lb, a)
    {
        sec.lbt = (lb - 1.0) * (1.0 - Math.exp(-a * inp.time)) + 1.0;
        ptr.rost = (hrost + brost) / (sec.lbt * 2.0);
        return ((hd + bd) / (2.0 * sec.lbt));
    }

    self.spread_distance = function (inp, ptr, a)
    {
        ptr.rost = ptr.ros * (1.0 - Math.exp(-a * inp.time));
        return (ptr.ros * (inp.time + (Math.exp(-a * inp.time) / a) - 1.0 / a));
    }

    self.time_to_crown = function (ros, rso, a)
    {
        var ratio;
        if (ros > 0)
            ratio = rso / ros;
        else
            ratio = 1.1;
        if (ratio > 0.9 && ratio <= 1.0)
            ratio = 0.9;
        if (ratio < 1.0)
            return (int)(Math.log(1.0 - ratio) / -a);
        return (99);
    }
    return self;
}

var FuelNonMixed = function(cover, fueltype, a, b, c, q, bui0, cbh, cfl, isOpen)
{
    var self = new FuelType(cover, fueltype, a, b, c, q, bui0, cbh, cfl, isOpen);
    self.isf_calc = function (inp, at, isi)
    {
        var rsz = self.ros_calc(inp, isi);
        var rsf = rsz * at.sf;
        return self.limit_isf(1.0, rsf);
    };
    return self;
};


var FuelGrass = function (fueltype, a, b, c, q, bui0, cbh, cfl)
{
    var self = new FuelType('n', fueltype, a, b, c, q, bui0, cbh, cfl, true);

    self.surf_fuel_consump = function (inp)
    {
        return inp.gfl;
    }


    self.base_mult = function (inp)
    {
        return (inp.cur >= 58.8) ?
               (0.176 + 0.02 * (inp.cur - 58.8)) :
               (0.005 * (Math.exp(0.061 * inp.cur) - 1.0));
    }

    self.isf_calc = function (inp, at, isi)
    {
        var mu = self.base_mult(inp);

        var rsz = self.ros_calc_mult(mu, isi);
        if (mu < 0.001) // to have some value here
            mu = 0.001;
        
        var rsf = rsz * at.sf;

        return self.limit_isf(mu, rsf);
    }

    self.ros_calc_mult = function (mult, isi)
    {
        return mult * (a * Math.pow((1.0 - Math.exp(-1.0 * b * isi)), c));
    }

    self.ros_calc = function (inp, isi)
    {
        return self.ros_calc_mult(self.base_mult(inp), isi);
    }
    
    self.l_to_b = function (ws)
    {
        return (ws < 1.0 ? 1.0 : (1.1 * Math.pow(ws, 0.464)));
    }
    return self;
}

var FuelO1a = function()
{
    var self = new FuelGrass("O1a", 190.0, 0.0310, 1.40, 1.000, 01, 0, 0.0);
    return self;
}

var FuelO1b = function()
{
    var self = new FuelGrass("O1b", 250.0, 0.0350, 1.7, 1.000, 1, 0, 0.0);
    return self;
}

var FuelMixed = function (fueltype, a, b, c, q, bui0, cbh, cfl, ros_mult, percent_mixed)
{
    var self = new FuelType('c', fueltype, a, b, c, q, bui0, cbh, cfl);
    self.ros_mult = ros_mult;
    self.percent_mixed = percent_mixed;
    
    self.surf_fuel_consump = function (inp)
    {
        return (5.0 * (1.0 - Math.exp(-0.0115 * inp.bui)));
    }

    self.get_mult = function ()
    {
        return self.percent_mixed / 100.0;
    }

    self.old_crown_consump = self.crown_consump;
    self.crown_consump = function (cfb)
    {
        return self.get_mult() * self.old_crown_consump(cfb);
    }

    self.ros_d1 = function (isi)
    {
        return FuelTypes["D1"].ros_basic(isi);
    }
    
    self.ros_calc = function (inp, isi)
    {
        var mult = self.get_mult();
        return mult * self.ros_basic(isi) + self.ros_mult * (1.0 - mult) * self.ros_d1(isi);
    }
    
    self.isf_d1 = function (at, isi)
    {
        var d1 = FuelTypes["D1"];
        var rsf_d1 = at.sf * (self.ros_mult * d1.a) * Math.pow((1.0 - Math.exp(-1.0 * d1.b * isi)), d1.c);

        return d1.limit_isf(self.ros_mult, rsf_d1);
    }

    self.isf_calc = function (inp, at, isi)
    {
        var rsf_max = at.sf * self.ros_basic(isi);
        var mult = self.get_mult();
        return (mult * self.limit_isf(1.0, rsf_max) + (1.0 - mult) * self.isf_d1(at, isi));
    }
    return self;
}

var FuelMixedWood = function (fueltype, a, b, c, q, bui0, cbh, cfl, ros_mult, percent_conifer)
{
    var self = new FuelMixed(fueltype, a, b, c, q, bui0, cbh, cfl, ros_mult, percent_conifer);

    self.old_surf_fuel_consump = self.surf_fuel_consump;
    self.surf_fuel_consump = function (inp)
    {
        var sfc_c2 = self.old_surf_fuel_consump(inp);
        var sfc_d1 = 1.5 * (1.0 - Math.exp(-0.0183 * inp.bui));
        var mult = get_mult();
        return mult * sfc_c2 + (1.0 - mult) * sfc_d1;
    }
    return self;
}

var FuelMixedDead = function (fueltype, a, b, c, q, bui0, cbh, cfl, ros_mult, percent_dead_fir)
{
    var self = new FuelMixed(fueltype, a, b, c, q, bui0, cbh, cfl, ros_mult, percent_dead_fir);
    return self;
}

var FuelM1 = function (percent_conifer)
{
    var self = new FuelMixedWood("M1", 110.0, 0.0282, 1.5, 0.80, 50, 6, 0.80, 1.0, percent_conifer);
    return self;
}

var FuelM2 = function (percent_conifer)
{
    var self = new FuelMixedWood("M2", 110.0, 0.0282, 1.5, 0.80, 50, 6, 0.80, 0.2, percent_conifer);
    return self;
}

var FuelM3 = function (percent_dead_fir)
{
    var self = new FuelMixedDead("M3", 120.0, 0.0572, 1.4, 0.80, 50, 6, 0.80, 1.0, percent_dead_fir);
    return self;
}

var FuelM4 = function (percent_dead_fir)
{
    var self = new FuelMixedDead("M4", 100.0, 0.0404, 1.48, 0.80, 50, 6, 0.80, 0.2, percent_dead_fir);
    return self;
}

var FuelD2 = function()
{
    var self = new FuelNonMixed('n', "D2", 6.0, 0.0232, 1.6, 0.90, 32, 0, 0.0, false);
    
    self.surf_fuel_consump = function (inp)
    {
        return (inp.bui >= 80 ? 1.5 * (1.0 - Math.exp(-0.0183 * inp.bui)) : 0.0);
    };
    
    self.ros_calc = function (inp, isi)
    {
        if (inp.bui >= 80)
        {
            return self.ros_basic(isi);
        }   
        return (0.0);
    }
    return self;
}

var FuelD1 = function()
{
    var self = new FuelConifer("D1", 30.0, 0.0232, 1.6, 0.90, 32, 0, 0.0);
    
    self.surf_fuel_consump = function (inp)
    {
        return 1.5 * (1.0 - Math.exp(-0.0183 * inp.bui));
    }
    return self;
}

var FuelConifer = function (fueltype, a, b, c,  q, bui0, cbh, cfl, isOpen)
{
    var self = new FuelNonMixed('c', fueltype, a, b, c, q, bui0, cbh, cfl, isOpen);

    self.ros_calc = function (inp, isi)
    {
        return self.ros_basic(isi);
    }
    return self;
}

var FuelSlash = function (fueltype, a,  b, c, q, bui0, cbh, cfl, c_a, c_b, c_c, c_d)
{
    var self = new FuelConifer(fueltype, a, b, c, q, bui0, cbh, cfl, true)
    self.c_a = c_a;
    self.c_b = c_b;
    self.c_c = c_c;
    self.c_d = c_d;

    self.surf_fuel_consump = function (inp)
    {
        var ffc = self.c_a * (1.0 - Math.exp(self.c_b * inp.bui));
        var wfc = self.c_c * (1.0 - Math.exp(self.c_d * inp.bui));
        return (ffc + wfc);
    }
    return self;
}

var FuelS1 = function ()
{
    var self = new FuelSlash("S1", 75.0, 0.0297, 1.3, 0.75, 38, 0, 0.0, 4.0, -0.025, 4.0, -0.034);
    return self;
}

var FuelS2 = function ()
{
    var self = new FuelSlash("S2", 40.0, 0.0438, 1.7, 0.75, 63, 0, 0.0, 10.0, -0.013, 6.0, -0.060);
    return self;
}

var FuelS3 = function ()
{
    var self = new FuelSlash("S3", 55.0, 0.0829, 3.2, 0.75, 31, 0, 0.0, 12.0, -0.0166, 20.0, -0.0210);
    return self;
}

var FuelC1 = function ()
{
    var self = new FuelConifer("C1", 90.0, 0.0649, 4.5, 0.90, 72, 2, 0.75, true);

    self.surf_fuel_consump = function (inp)
    {
        /*       sfc=1.5*(1.0-exp(-0.23*(ffmc-81.0)));*/
        var sfc = (inp.ffmc > 84) ?
                    (0.75 + 0.75 * Math.Sqrt(1 - Math.exp(-0.23 * (inp.ffmc - 84)))) :
                    (0.75 - 0.75 * Math.Sqrt(1 - Math.exp(0.23 * (inp.ffmc - 84))));
        return (sfc >= 0 ? sfc : 0.0);
    }
    return self;
}

var FuelC2 = function ()
{
    var self = new FuelConifer("C2", 110.0, 0.0282, 1.5, 0.70, 64, 3, 0.80);
    
    self.surf_fuel_consump = function (inp)
    {
        return (5.0 * (1.0 - Math.exp(-0.0115 * inp.bui)));
    }
    return self;
}

var FuelJackpine = function (fueltype, a, b, c, q, bui0, cbh, cfl)
{
    var self = new FuelConifer(fueltype, a, b, c, q, bui0, cbh, cfl);

    self.surf_fuel_consump = function (inp)
    {
        return (5.0 * Math.pow((1.0 - Math.exp(-0.0164 * inp.bui)), 2.24));
    }
    return self;
}

var FuelC3 = function ()
{
    var self = new FuelJackpine("C3", 110.0, 0.0444, 3.0, 0.75, 62, 8, 1.15);
    return self;
}

var FuelC4 = function ()
{
    var self = new FuelJackpine("C4", 110.0, 0.0293, 1.5, 0.80, 66, 4, 1.20);
    return self;
}

var FuelPine = function (fueltype, a, b, c, q, bui0, cbh, cfl)
{
    var self = new FuelConifer(fueltype, a, b, c, q, bui0, cbh, cfl);
    
    self.surf_fuel_consump = function (inp)
    {
        return (5.0 * Math.pow((1.0 - Math.exp(-0.0149 * inp.bui)), 2.48));
    }
    return self;
}

var FuelC5 = function ()
{
    var self = new FuelPine("C5", 30.0, 0.0697, 4.0, 0.80, 56, 18, 1.20);
    return self;
}

var FuelC6 = function ()
{
    var self = new FuelPine("C6", 30.0, 0.0800, 3.0, 0.80, 62, 7, 1.80);

    self.final_ros = function (fmc, isi, cfb, rss)
    {
        var rsc = self.foliar_mois_effect(isi, fmc);
        return rss + cfb * (rsc - rss);
    }
    return self;
}

var FuelC7 = function ()
{
    var self = new FuelConifer("C7", 45.0, 0.0305, 2.0, 0.85, 106, 10, 0.50);
    
    self.surf_fuel_consump = function (inp)
    {
        var ffc = 2.0 * (1.0 - Math.exp(-0.104 * (inp.ffmc - 70.0)));
        if (ffc < 0)
            ffc = 0.0;
        var wfc = 1.5 * (1.0 - Math.exp(-0.0201 * inp.bui));
        return (ffc + wfc);
    }
    return self;
}

var FuelTypes =
{
    "C1": new FuelC1(),
    "C2": new FuelC2(),
    "C3": new FuelC3(),
    "C4": new FuelC4(),
    "C5": new FuelC5(),
    "C6": new FuelC6(),
    "D1": new FuelD1(),
    "M125": new FuelM1(25),
    "M150": new FuelM1(50),
    "M175": new FuelM1(75),
    "M225": new FuelM2(25),
    "M250": new FuelM2(50),
    "M275": new FuelM2(75),
    "M330": new FuelM3(30),
    "M360": new FuelM3(60),
    "M3100": new FuelM3(100),
    "M430": new FuelM4(30),
    "M460": new FuelM4(60),
    "M4100": new FuelM4(100),
    "O1a": new FuelO1a(),
    "O1b": new FuelO1b(),
    "S1": new FuelS1(),
    "S2": new FuelS2(),
    "C7": new FuelC7(),
    "D2": new FuelD2(),
    "S3": new FuelS3()
};

function GetFuel(name)
{
    if (!(name in FuelTypes))
    {
        return null;
    }
    return FuelTypes[name];
}

function zero_main(m)
{
    m.sfc = 0.0;
    m.csi = 0.0;
    m.rso = 0.0;
    m.fmc = 0;
    m.sfi = 0.0;
    m.rss = 0.0;
    m.isi = 0.0;
    m.be = 0.0;
    m.sf = 1.0;
    m.raz = 0.0;
    m.wsv = 0.0;
    m.ff = 0.0;
    m.covertype = ' ';
}

function zero_sec(s)
{
    s.lb = 0.0;
    s.area = 0.0;
    s.perm = 0.0;
    s.pgr = 0.0;
}

function zero_fire(a)
{
    a.ros = 0.0;
    a.dist = 0.0;
    a.rost = 0.0;
    a.cfb = 0.0;
    a.fi = 0.0;
    a.fc = 0.0;
    a.cfc = 0.0;
    a.time = 0.0;
    a.fd = ' ';
}
