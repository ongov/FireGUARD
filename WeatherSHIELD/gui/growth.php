<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
            <title>WeatherSHIELD</title>
            <link rel="icon" href="favicon.png" type="image/vnd.microsoft.icon">
            
            <!-- Bootstrap -->
            <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
            <!-- deal with grid sizes 480px <= x <= 768px -->
            <link href="bootstrap/css/bootstrap_ms.css" rel="stylesheet">

            <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
            <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
            <!--[if lt IE 9]>
              <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
              <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
            <![endif]-->
            
            <link rel="stylesheet" href="css/styles.css">
            
        <script type='text/javascript' src='js/jquery-1.11.3.min.js'></script>
        <script type="text/javascript" src="js/canvg.js"></script>
        <script type="text/javascript" src="js/rgbcolor.js"></script>
        <script type="text/javascript" src="js/jcanvas.js"></script>
        <script src="js/DateCalculations.js"> </script>
        <script src="js/calc_fwi.js"></script>
        <script src="js/weatherSHIELD_1.js"> </script>
        
        <script src="js/calc_fbp.js"> </script>
<script type='text/javascript'>
var MAIN = null;

class Position {
    constructor(easting, northing)
    {
        // HACK: instead of checking that points are within TOLERANCE distance of each other just round them
        this.easting = MAIN.roundToTolerance(easting);
        this.northing = MAIN.roundToTolerance(northing);
    }
    
    compareTo(b)
    {
        // sort so we can do convex hull algorithm
        return this.easting == b.easting ? this.northing - b.northing : this.easting - b.easting;
    }
    
    cross(a, b)
    {
        return (a.easting - this.easting)*(b.northing - this.northing) - (a.northing - this.northing)*(b.easting - this.easting);
    }
    
    static compare(a, b)
    {
        return a.compareTo(b);
    }
}

class Point extends Position {
    constructor(easting, northing, isFake)
    {
        super(easting, northing);
        // HACK: do this so undefined becomes false
        this.real = !isFake;
        this.x = toX(easting);
        this.y = toY(northing);
        var x = Math.floor(this.x);
        var y = Math.floor(this.y);
        // HACK: for now we'll clip these to the bounds
        this.cell = ((x == Math.max(0, Math.min(x, MAIN.CELLS.length - 1))) && y == Math.max(0, Math.min(y, MAIN.CELLS[x].length - 1))) ? MAIN.CELLS[x][y] : null;
    }
    
    drawPoint(lyr)
    {
        var bounds = MAIN.BOUNDS;
        lyr.drawRect({
            layer: true,
            groups: ['points'],
            strokeStyle: 'blue',
            strokeWidth: 1,
            x: this.x * bounds.cellSize,
            // HACK: need to flip y since it's from bottom left, not top left
            y: bounds.height - (this.y * bounds.cellSize),
            width: 1,
            height: 1
        });
    }
    
    static isReal(point)
    {
        return point.real;
    }
}

class FakePoint extends Point {
    // HACK: just so we can imply !real instead of needing to specify
    constructor(easting, northing)
    {
        super(easting, northing, true);
    }
}

class Cell extends Position {
    constructor(x, y)
    {
        var bounds = MAIN.BOUNDS;
        var easting = bounds.EASTINGS[x];
        var northing = bounds.NORTHINGS[y];
        super(easting, northing);
        var centroidEasting = easting + 0.5 * bounds.cellLength;
        var centroidNorthing = northing + 0.5 * bounds.cellLength;
        this.burning = false;
        this.burned = false;
        this.out = false;
        this.fuelType = 'C2';
        this.x = x;
        this.y = y;
        this.centroid = new FakePoint(centroidEasting, centroidNorthing);
        this.name = 'cell_' + x + '_' + y;
        this.points = new PointList();
        this.neighbours = [];
    }
    
    // HACK: so we can call this with filter()
    static isBurning(cell)
    {
        return cell.burning;
    }
    
    static isBurned(cell)
    {
        return cell.burned;
    }
    
    getCellColor()
    {
        return this.CELL_COLORS[this.out ? 'Out' : this.burned ? 'Burned' : this.burning ? 'Burning' : this.fuelType];
    }
    
    colorCell()
    {
        var layer = MAIN.LAYERS.LYR_ACTIVE_CELLS.getLayer(this.name);
        if (layer)
        {
            layer.fillStyle = this.getCellColor();
        }
        else
        {
            this.drawCell(MAIN.LAYERS.LYR_ACTIVE_CELLS)
        }
    }
    
    drawCell(output)
    {
        var bounds = MAIN.BOUNDS;
        var color = this.getCellColor();
        output.drawRect({
            layer: true,
            groups: ['cells'],
            name: this.name,
            fillStyle: color,
            strokeStyle: 'blue',
            strokeWidth: 0.15,
            x: this.x * bounds.cellSize,
            // HACK: need to flip y since it's from bottom left, not top left
            y: bounds.height - ((this.y + 1) * bounds.cellSize),
            fromCenter: false,
            width: bounds.cellSize,
            height: bounds.cellSize
        });
    }
    
    isFuel()
    {
        return this.fuelType != 'Water';
    }
    
    convexHull()
    {
        // HACK: if < 4 points then include them all because they are a point, line or triangle
        if (this.points.array.length < 4)
        {
            return this.points.array;
        }
        
        var cur_points = this.points;
        // HACK: add in points from burned cells so that points along burned edges don't get included
        var fake_points = [];
        // these should be in order as well because the cells are in order and then the points are
        var burnedNeighbours = this.neighbours.filter(Cell.isBurned);
        for (var n = 0; n < burnedNeighbours.length; n++)
        {
            var p = burnedNeighbours[n].centroid;
            // add centroid so points along edge are excluded
            // these are already sorted because neighbours are
            fake_points.push(p);
            // there's no way for this to not be sorted, so don't check vs -1
            cur_points.insertNext(p);
        }
        
        var hull_points = cur_points.convexHull();
        this.points.array = hull_points.filter(Point.isReal);
        return this.points.array;
    }
}
// HACK: no way to set class variables with class syntax
Cell.prototype.CELL_COLORS = {
    'Out': makeRGBA(89, 120, 89, 1.0),
    'Burned': makeRGBA(166, 145, 114, 1.0),
    'Burning': makeRGBA(216, 170, 139, 1.0),
    'Water': makeRGBA(178, 178, 255, 1.0),
    'C2': makeRGBA(178, 240, 178, 1.0)
};

class List {
    constructor()
    {
        this.array = [];
        this.last = 0;
    }
    
    push(value)
    {
        return this.array.push(value);
    }
    
    findPosition(value, i)
    {
        // NOTE: need to give index i as a parameter
        var compareResult = -1;
        var values = this.array;
        // NOTE: compareResult is being set in this comparison on purpose so we have it after loop quit
        while (i < values.length && (0 > (compareResult = values[i].compareTo(value))))
        {
            i++;
        }
        this.last = i;
        // always return the position the cell is now even if it was already there
        return compareResult;
    }
    
    insertPosition(value, i)
    {
        var compareResult = this.findPosition(value, i);
        if (0 != compareResult)
        {
            // cells are not equal within tolerances so we add this one
            this.array.splice(this.last, 0, value);
            return true;
        }
        return false;
    }
    
    insertNext(value)
    {
        return this.insertPosition(value, this.last);
    }
    
    removePosition(value, i)
    {
        var compareResult = this.findPosition(value, i);
        if (0 == compareResult)
        {
            // found a match so remove it
            this.array.splice(this.last, 0);
            return true;
        }
        return false;
    }
    
    removeNext(value)
    {
        return this.removePosition(value, this.last);
    }
}

class PointList extends List {
    constructor()
    {
        super();
    }
    
    convexHull()
    {
        var points = this.array;
        // HACK: if < 4 points then include them all because they are a point, line or triangle
        if (points.length < 4)
        {
            return points;
        }
        
        // should be sorted already
        
        // https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
        // assume points are already sorted by Y,X
        var lower = [];
        for (var i = 0; i < points.length; i++) {
            while (lower.length >= 2 && lower[lower.length - 2].cross(lower[lower.length - 1], points[i]) <= 0) {
                lower.pop();
            }
            lower.push(points[i]);
        }
        
        var upper = [];
        for (var i = points.length - 1; i >= 0; i--) {
            while (upper.length >= 2 && upper[upper.length - 2].cross(upper[upper.length - 1], points[i]) <= 0) {
                upper.pop();
            }
            upper.push(points[i]);
        }
        
        upper.pop();
        lower.pop();
        // NOTE: these are NOT sorted
        return lower.concat(upper);
    }
}

class MainList extends PointList {
    constructor()
    {
        super();
        this.cellsBurning = new CellList();
        this.cellsBurned = new CellList();
        this.cellsOut = new CellList();
        this.cellsRedraw = new CellList();
    }
    
    drawPoints(lyr)
    {
        lyr.clearCanvas();
        for (var p = 0; p < this.array.length; p++)
        {
            var point = this.array[p];
            point.drawPoint(lyr);
        }
    }
    
    checkPointCellsBurning()
    {
        var points = this.array;
        for (var p = 0; p < points.length; p++)
        {
            var cell = points[p].cell;
            // don't add if already burning
            if (!cell.burning)
            {
                cell.burning = true;
                this.cellsBurning.insertNext(cell);
                this.cellsRedraw.insertNext(cell);
            }
        }
    }
    
    static checkNotBurned(cell, mainList)
    {
        // if every neighbour is burned then this is out
        cell.burned = cell.neighbours.every(Cell.isBurning);
        if (cell.burned)
        {
            mainList.cellsBurned.insertNext(cell);
            mainList.cellsRedraw.insertNext(cell);
        }
        return !cell.burned;
    }
    
    static checkNotOut(cell, mainList)
    {
        // if every neighbour is burned then this is out
        cell.out = cell.neighbours.every(Cell.isBurned);
        if (cell.out)
        {
            // don't want cell in redraw cells because we're going to remove it later anyway
            mainList.cellsOut.insertNext(cell);
            mainList.cellsRedraw.removeNext(cell);
        }
        return !cell.out;
    }
    
    setAndCheckPoints(new_points)
    {
        this.array = [];
        // only need to worry about cells that have something going on in them
        var burningCells = this.cellsBurning.array;
        for (var i = 0; i < burningCells.length; i++)
        {
            burningCells[i].points = new PointList();
        }
        var burnedCells = this.cellsBurned.array;
        for (var i = 0; i < burnedCells.length; i++)
        {
            burnedCells[i].points = new PointList();
        }
        // shouldn't be any points in out cells
        // NOTE: clear the layer in drawPoints()

        if (0 == new_points.length)
        {
            return;
        }
        new_points.sort(Position.compare);
        var i = -1;
        // even though these are sorted, we want to use insert to check for equivalent points
        for (var p = 0; p < new_points.length; p++)
        {
            var point = new_points[p];
            if (!(point.cell.out || !point.cell.isFuel()))
            {
                // don't add a point to a out or non-fuel cell
                // if equivalent point already exists then don't add
                // either last point matches or this is new
                if (-1 == i || 0 != point.compareTo(this.array[i]))
                {
                    i++;
                    this.array.push(point);
                    // we know points are in order, so just append to cell points list
                    point.cell.points.push(point);
                }
            }
        }
        this.checkPointCellsBurning();
        // now every cell that is burning should be in cellsBurning
        this.cellsBurning.checkCells(MainList.checkNotBurned, this);
        this.cellsBurned.checkCells(MainList.checkNotOut, this);
    }
    
    redrawCells()
    {
        // length will be 0 if noRedraw since nothing was added
        for (var c = 0; c < this.cellsRedraw.array.length; c++)
        {
            this.cellsRedraw.array[c].colorCell();
        }
        this.cellsRedraw = new CellList();
        // add all out cells to that canvas
        for (var c = 0; c < this.cellsOut.array.length; c++)
        {
            var cell = this.cellsOut.array[c];
            cell.drawCell(MAIN.LAYERS.LYR_OUT_CELLS);
            MAIN.LAYERS.LYR_ACTIVE_CELLS.removeLayer(cell.name);
        }
        this.cellsOut = new CellList();
    }
    
    condenseByHull()
    {
        var points = this;
        var cell_points = {};
        var new_points = [];
        
        var doFullHull = Options.getFullHullFirstOn();
        
        // make a list of all cells we got points from
        var used_cells = [];
        if (doFullHull)
        {
            // do a hull of the whole fire, but then for every cell that's burning but wasn't included
            // do a hull of that cell
            var basic_hull = points.convexHull();
            // get a list of all the cells that were used by these points
            used_cells = basic_hull.map(function (point) {
                                            return point.cell;
                                        }).filter(
                                            function (value, index, self) {
                                                return self.indexOf(value) === index;
                                            });
            used_cells.sort(Position.compare);
            new_points.push(...basic_hull);
        }
        
        // find all the burning cells that weren't included
        
        var p = 0;
        var burningCells = this.cellsBurning.array;
        for (var c = 0; c < burningCells.length; c++)
        {
            var cell = burningCells[c];
            // find the next cell in used_cells that's equal to or after this cell
            while (doFullHull && p < used_cells.length && 0 < cell.compareTo(used_cells[p]))
            {
                p++;
            }
            if (!doFullHull || (used_cells.length == p) || cell != used_cells[p])
            {
                // this cell doesn't have any included points
                if (0 < cell.points.array.length)
                {
                    // cell should always be at least burning
                    if (cell.out)
                    {
                        // get rid of all the points in this cell because it's burned
                        cell.points = new PointList();
                    }
                    else
                    {
                        new_points.push(...cell.convexHull());
                    }
                }
            }
        }
        
        // we set all the cell points above so we can just sort the list of points and set it
        new_points.sort(Position.compare);
        this.array = new_points;
    }
}

class CellList extends List {
    constructor()
    {
        super();
    }
    
    checkCells(fct, mainList)
    {
        // we have a list of all cells that had points put in them, so check those
        this.last = 0;
        this.array = this.array.filter(function (cell)
                                    {
                                        return fct(cell, mainList);
                                    });
    }
}

class Options {
    // HACK: all static methods - just to encapsulate these
    static getAngleSkew()
    {
        return parseFloat($('#skew').val());
    }
    
    static getHeadAngle()
    {
        return parseFloat($('#headAngle').val());
    }
    
    static getProfileOn()
    {
        return $('#profile').is(':checked');
    }
    
    static getProfileDrawOn()
    {
        return $('#profileDraw').is(':checked');
    }
    
    static getAutoGrowthOn()
    {
        return $('#autogrow').is(':checked');
    }
    
    static getShowEachOn()
    {
        return $('#showEach').is(':checked');
    }
    
    static getFullHullFirstOn()
    {
        return $('#fullHull').is(':checked');
    }
    
    static getNumberOfAngles()
    {
        return parseInt($('#numberOfAngles').val());
    }
    
    static getROSHead()
    {
        return parseFloat($('#rosHead').val());
    }
    
    static getROSBack()
    {
        return parseFloat($('#rosBack').val());
    }
    
    static getLBRatio()
    {
        return parseFloat($('#lbRatio').val());
    }
    
    static getDirection()
    {
        return parseFloat($('#direction').val());
    }
    
    static getDuration()
    {
        return parseFloat($('#duration').val());
    }
    
    static getTolerance()
    {
        return parseFloat($('#tolerance').val());
    }
    
    static getShowLabels()
    {
        return $('#labels').is(':checked');
    }
    
    static getGenerations()
    {
        return parseInt($('#generations').val());
    }
    
    static getShowProgress()
    {
        return $('#progress').is(':checked');
    }
}

function toBasemap(easting, northing)
{
    return (Math.floor(easting / 10000) * 1000) + Math.floor(northing / 10000);
}

function toX(easting)
{
    var bounds = MAIN.BOUNDS;
    return (easting - bounds.utmLeft) / bounds.cellLength;
}

function toY(northing)
{
    var bounds = MAIN.BOUNDS;
    return (northing - bounds.utmBottom) / bounds.cellLength;
}

// NOTE: overridden in some fuel types
function l_to_b(ws)
{
    return (1.0 + 8.729 * Math.Pow(1.0 - Math.Exp(-0.030 * ws), 2.155));
}

function calcGrowth(ROSHead, ROSBack, lb, numberOfAngles, directionOfSpread, durationOfSpread)
{
    var directionMax = toRadians(directionOfSpread); // radians
    var intSlope = 0; // % slope
    var aspect = 180; // degrees
    var new_points = [];
    var directions = [];
    // try out directions except skewed based on direction of spread
    // want to focus more on head spread since that will be farther (assuming ROSHead > ROSBack)
    var headRadians = toRadians(Options.getHeadAngle());
    var backRadians = 2 * Math.PI - headRadians;
    var midAngleLeft = directionMax - headRadians / 2;
    var midAngleRight = directionMax + headRadians / 2;
    var curNum = Math.floor(numberOfAngles / (2 * Math.pow((ROSHead / ROSBack), Options.getAngleSkew())));
    for (var i = 0; i < curNum; i++)
    {
        directions.push(midAngleRight + (backRadians) * (i / curNum)); // degrees
    }
    curNum = numberOfAngles - curNum;
    for (var i = 0; i < curNum; i++)
    {
        directions.push(midAngleLeft + (headRadians) * (i / curNum)); // degrees
    }
    for (var i = 0; i < numberOfAngles; i++)
    {
        var dblDirectionOfROS = directions[i];
        var ros = CalcROSHorizontal(ROSHead, ROSBack, lb, dblDirectionOfROS, directionMax, aspect, intSlope); // m/s
        // need to generate a point in that direction at the proper distance
        var distance = durationOfSpread * ros; // m
        // need to convert from distance/direction to x/y vectors
        var angle = dblDirectionOfROS;
        var dblX = distance * Math.sin(angle);
        var dblY = distance * Math.cos(angle);
        new_points.push({
            x: dblX,
            y: dblY
        });
    }
    return new_points;
}

function toRadians(x)
{
    return x * (Math.PI / 180);
}

function toDegrees(x)
{
    return x * (180 / Math.PI);
}

function CalcROSHorizontal(ROSHead, ROSBack, lb, dblDirectionOfROS, directionMax, aspect, intSlope)
{
    var ROSAtDirection = null;
    // the angle for the formula is the difference between:
    // - the angle of maximum ROS, and
    // - the angle of the needed ROS
    // the sign does not matter, because the formula is symmetrical
    // AngleOfDirection is in radians, DirectionMax in degrees
    // dblTheta is in radians
    var dblTheta = dblDirectionOfROS - directionMax;

    // for dblTheta = 90 or 270 degrees, there is a zero divide below;
    // in these cases, add a small amount to dblTheta to avoid dividing
    // by zero; this adds about 0.115 degrees
    // If dblTheta is too close to 90 or 270 degrees, then add enough radians to
    // make dblTheta far from 90 or 270 degrees whether dblTheta was
    // originally greater or lesser than 90 or 270 degrees
    //WB codes
    if (Math.abs(dblTheta) < 0.001)
    {
        ROSAtDirection = ROSHead;
    }
    else if (Math.abs(Math.abs(dblTheta) - Math.PI) < 0.001)
    {
        ROSAtDirection = ROSBack;
    }
    else
    {
        if ((Math.abs(Math.abs(dblTheta) - (Math.PI / 2.0)) < 0.001)
            || (Math.abs(Math.abs(dblTheta) - (3.0 * Math.PI / 2.0)) < 0.001))
        {
            dblTheta = dblTheta + 0.002;
        }
        var a = (ROSHead + ROSBack) / 2.0;
        var c = a - ROSBack;
        var b = a / lb;
        
        // the angle dblTheta is in radians; angle to cos and sin must be in radians
        var cang = Math.cos(dblTheta);
        var sang = Math.sin(dblTheta);
        var CT = (b*cang*Math.sqrt(b*b*cang*cang + (a*a - c*c)*sang*sang) - a*c*sang*sang)/
                   (b*b*cang*cang + a*a*sang*sang);
        var x = a*CT;
        ROSAtDirection = Math.abs((x + c)/cang);
    }
    //WB codes ends

    //using Parameter::PI;

    // Convert the slope from percent (SlopePct) to radians (SlopeRad)
    // By definition:
    //    [1] SlopePct = y / x * 100%, where y is the "rise" and x is the "run"
    //    [2] Tan(SlopeRad) = y / x
    // To convert SlopePct to SlopeRad:
    // Rearrange equation [1] to solve for y / x:
    //    [3] y / x = SlopePct / 100%
    // Rearrange equation [2] to solve for SlopeRad:
    //    [4] SlopeRad = arctan(y / x)
    // Substitute equation [3] into equation [4], eliminating y / x
    //    [5] SlopeRad = arctan(SlopePct / 100)
    // If the slope is zero or low enough, skip this adjustment
    // Note that this check will also affect the bad data of a negative slope
    if (intSlope < 1)
    {
        // do nothing
    }
    else
    {
        var dblSlopeRadians = Math.atan(intSlope / 100.0);

        // calculate the minor semi-axis of the ellipse
        var dblBSemi = Math.cos(dblSlopeRadians);

        // rotate the arbitrary angle back to its position on the unrotated
        // ellipse
        var dblArbAngleUnrot = dblDirectionOfROS - aspect;

        var tanUnrot = Math.tan(dblArbAngleUnrot);
        // calculate y and x, the co-ordinates on the ellipse perimeter
        var dblY = dblBSemi / Math.sqrt((dblBSemi * tanUnrot) * (dblBSemi * tanUnrot) + 1.0);
        var dblX = dblY * tanUnrot;
        var dblDistance = Math.sqrt(dblX * dblX + dblY * dblY);
        ROSAtDirection *= dblDistance;
    }
    
    return ROSAtDirection;
}

class Layers {
    constructor()
    {
        // original cells canvas
        this.OUTPUT = $('#lyrOutput');
        // points canvas
        this.LYR_POINTS = $('#lyrPoints');
        // basemaps canvas
        this.LYR_BASEMAPS = $('#lyrBasemaps');
        // burning/burned cells canvas
        this.LYR_ACTIVE_CELLS = $('#lyrActiveCells');
        // out cells canvas
        this.LYR_OUT_CELLS = $('#lyrOutCells');
        MAIN.BOUNDS = new Bounds(this.OUTPUT, 100, 100, 459320, 5658230, 1000)
        var bounds = MAIN.BOUNDS;
        var CELLS = [];
        MAIN.CELLS = CELLS;
        this.CELLS = MAIN.CELLS;
        
        for (var i = 0; i < bounds.xCells; i++)
        {
            CELLS[i] = [];
            for (var j = 0; j < bounds.yCells; j++)
            {
                CELLS[i][j] = new Cell(i, j);
            }
        }
        
        // make some lakes & boundaries
        this.addLake(50, 60, 8, 3, 1.5, 256, 135, 1500);
        this.addLake(30, 80, 5, 5, 1.0, 256, 45, 900);
        this.addLake(60, 80, 10, 2, 2.0, 256, 90, 4000);
        this.addLake(20, 20, 20, 2, 3.0, 1024, 80, 6000);
        
        //NOTE: this has to be after adding the lakes because otherwise everything is fuel
        // now let's set up the neighbours for each cell
        for (var x = 0; x < bounds.xCells; x++)
        {
            for (var y = 0; y < bounds.yCells; y++)
            {
                var cell = CELLS[x][y];
                for (var i = Math.max(x - 1, 0); i <= Math.min(x + 1, bounds.xCells - 1); i++)
                {
                    for (var j = Math.max(y - 1, 0); j <= Math.min(y + 1, bounds.yCells - 1); j++)
                    {
                        // only include neighbours that are fuel
                        if ((i != x || j != y) && CELLS[i][j].isFuel())
                        {
                            // these have to be in order, so just push
                            cell.neighbours.push(CELLS[i][j]);
                        }
                    }
                }
            }
        }
        this.POINTS = new MainList();
    }
    
    addLake(i, j, ROSHead, ROSBack, lb, numAngles, direction, duration)
    {
        var offsets = calcGrowth(ROSHead, ROSBack, lb, numAngles, direction, duration);
        var point = this.CELLS[i][j].centroid;
        var lake_cells = new CellList();
        for (var o = 0; o < offsets.length; o++)
        {
            var offset = offsets[o];
            var new_point = new FakePoint(offset.x + point.easting, offset.y + point.northing);
            if (new_point.cell)
            {
                lake_cells.insertPosition(new_point.cell, 0);
            }
        }
        
        var c = 0;
        var cells = lake_cells.array;
        while (c < cells.length)
        {
            var new_cell = cells[c];
            new_cell.fuelType = 'Water';
            c++;
            var minY = new_cell.y;
            var maxY = new_cell.y;
            while (c < cells.length && (new_cell.x == cells[c].x))
            {
                maxY = cells[c].y;
                c++;
            }
            // these are in a line, so color all cells between them
            for (var y = minY; y < maxY; y++)
            {
                this.CELLS[new_cell.x][y].fuelType = 'Water';
            }
        }
    }
    
    clear()
    {
        var bounds = MAIN.BOUNDS;
        this.LYR_OUT_CELLS.removeLayerGroup('cells');
        this.LYR_OUT_CELLS.clearCanvas();
        this.LYR_ACTIVE_CELLS.removeLayerGroup('cells');
        this.LYR_ACTIVE_CELLS.clearCanvas();
        this.LYR_POINTS.removeLayerGroup('points');
        this.LYR_POINTS.clearCanvas();
        this.OUTPUT.clearCanvas();
        this.OUTPUT.drawRect({
            // HACK: has to be a layer or it disappears on mouseover
            layer: true,
            fillStyle: 'white',
            x: 0,
            y: 0,
            width: bounds.xMax * 4,
            height: bounds.yMax * 4
        });
    }
    
    drawCells()
    {
        var bounds = MAIN.BOUNDS;
        for (var i = 0; i < bounds.xCells; i++)
        {
            for (var j = 0; j < bounds.yCells; j++)
            {
                this.CELLS[i][j].drawCell(this.OUTPUT);
            }
        }
    }
    
    drawBasemaps()
    {
        var bounds = MAIN.BOUNDS;
        if (this.LYR_BASEMAPS.getLayerGroup('basemap_labels'))
        {
            // only need to do this once
            return;
        }
        var minLeft = Math.floor(bounds.utmLeft / 10000) * 10000;
        var minBottom = Math.floor(bounds.utmBottom / 10000) * 10000;
        var basemapSizeMult = (10000 / bounds.cellLength)
        var basemapSize = (bounds.cellLength * basemapSizeMult);
        var basemapFill = makeRGBA(0, 0, 0, 0);
        for (var x = minLeft; x <= bounds.utmRight + basemapSize; x += basemapSize)
        {
            for (var y = minBottom; y <= bounds.utmTop + basemapSize; y += basemapSize)
            {
                var ptX = Math.floor(toX(x));
                var ptY = Math.floor(toY(y));
                this.LYR_BASEMAPS.drawRect({
                    layer: true,
                    groups: ['basemap_cells'],
                    fillStyle: basemapFill,
                    strokeStyle: 'black',
                    strokeWidth: 0.3,
                    x: ptX * bounds.cellSize,
                    // HACK: need to flip y since it's from bottom left, not top left
                    y: bounds.height - (ptY * bounds.cellSize),
                    fromCenter: false,
                    width: bounds.cellSize * (basemapSizeMult),
                    height: bounds.cellSize * (basemapSizeMult)
                });
                this.LYR_BASEMAPS.drawText({
                    layer: true,
                    groups: ['basemap_labels'],
                    text: toBasemap(x, y),
                    fontSize: 12,
                    x: (ptX + basemapSizeMult / 2) * bounds.cellSize,
                    y: bounds.height - ((ptY + basemapSizeMult / 2) * bounds.cellSize),
                    fillStyle: 'lightblue',
                    strokeStyle: 'blue',
                    strokeWidth: 1
                });
            }
        }
    }
    
    toggleLabels(value)
    {
        var showLabels = Options.getShowLabels();
        var basemap_labels = this.LYR_BASEMAPS.getLayerGroup('basemap_labels');
        for (var b = 0; b < basemap_labels.length; b++)
        {
            var layer = basemap_labels[b];
            layer.visible = showLabels;
        }
        this.LYR_BASEMAPS.drawLayers();
    }
    
    draw()
    {
        this.clear();
        this.drawCells();
        this.POINTS.drawPoints(this.LYR_POINTS);
    }
    
    redraw()
    {
        this.POINTS.redrawCells();
        // only draw at the end and not during calculations
        this.POINTS.drawPoints(this.LYR_POINTS);
        this.LYR_ACTIVE_CELLS.drawLayers();
    }
}

class Bounds {
    constructor(lyr, xCells, yCells, utmLeft, utmBottom, cellLength)
    {
        this.xMin = 0;
        this.xMax = lyr.innerWidth();
        this.yMin = 0;
        this.yMax = lyr.innerHeight();
        this.width = this.xMax - this.xMin;
        this.height = this.yMax - this.yMin;
        this.xCells = xCells;
        this.yCells = yCells;
        // cell side length in m
        this.cellLength = cellLength;
        // HACK: need to have corner exactly on a cell edge
        this.utmLeft = Math.floor(utmLeft / cellLength) * cellLength;
        this.utmBottom = Math.floor(utmBottom / cellLength) * cellLength;
        this.utmRight = utmLeft + ((xCells + 1) * cellLength);
        this.utmTop = utmBottom + ((yCells + 1) * cellLength);
        this.cellSize = this.width / xCells;
        this.EASTINGS = [];
        this.NORTHINGS = [];
        // want to add an extra cell onto these for convenience when checking things
        for (var i = -1; i <= this.xCells; i++)
        {
            this.EASTINGS[i] = this.utmLeft + i * this.cellLength;
        }
        for (var j = -1; j <= this.yCells; j++)
        {
            this.NORTHINGS[j] = this.utmBottom + j * this.cellLength;
        }
    }
}

class Main {
    constructor()
    {
        this.TOLERANCE = 1;  // 1 m
        this.CUR_GENERATION = 0;
        this.TOTAL_TIME = null;
        this.TOTAL_CALCULATION_TIME = null;
        this.TOTAL_DRAW_TIME = null;
        this.TIME_START = null;
        this.IS_PROFILING = false;
        this.PROFILE_DRAW = false;
        this.DONE = false;
        this.LAYERS = null;
        this.BOUNDS = null;
        this.MESSAGES = {};
    }
    
    roundToTolerance(v)
    {
        // HACK: assume TOLERANCE is set properly
        // round to center of TOLERANCE area so that if we go to block level it's all centroids
        return (Math.floor(v / this.TOLERANCE) + 0.5) * this.TOLERANCE;
    }
    
    doGrowth()
    {
        var cur_points = this.LAYERS.POINTS.array;
        var new_points = [];
        
        var duration = Options.getDuration();
        
        var offsets = calcGrowth(Options.getROSHead(), Options.getROSBack(), Options.getLBRatio(), Options.getNumberOfAngles(),  Options.getDirection(), duration);
        
        for (var p = 0; p < cur_points.length; p++)
        {
            var point = cur_points[p];
            // HACK: don't grow from burned cells
            if (!(point.cell.burned))
            {
                for (var o = 0; o < offsets.length; o++)
                {
                    var offset = offsets[o];
                    var new_point = new Point(offset.x + point.easting, offset.y + point.northing);
                    // HACK: don't burn into burned cells, but keep burning in current cell
                    if (new_point.cell && (!(new_point.cell.burned) || (new_point.cell == point.cell)))
                    {
                        new_points.push(new_point);
                    }
                }
            }
        }
        this.TOTAL_TIME += duration;
        this.setMessage('#totalTime', 'Total Duration: ' + this.TOTAL_TIME + 's');
        return new_points;
    }
    
    timeFunction(fct)
    {
        this.TIME_START = performance.now();
        // when condensing points have higher tolerance but make sure that it's always at least an int
        var shouldRedraw = fct();
        var timeEnd = performance.now();
        var calcTime = timeEnd - this.TIME_START;
        this.TOTAL_CALCULATION_TIME += calcTime;
        this.setMessage('#calcTime', 'Calculation time: ' + calcTime.toFixed(2) + 'ms current - ' + this.TOTAL_CALCULATION_TIME.toFixed(2) + 'ms total');
        // NOTE: don't want to profile drawing
        if (this.DONE && this.IS_PROFILING && !this.PROFILE_DRAW)
        {
            console.profileEnd();
        }
        if (shouldRedraw)
        {
            this.redraw();
        }
        if (this.DONE && this.IS_PROFILING && this.PROFILE_DRAW)
        {
            console.profileEnd();
        }
        if (this.DONE || Options.getShowProgress())
        {
            this.showMessages();
        }
    }
    
    cancelSubmit(fctName)
    {
        return (function (main)
        {
            return function(event)
            {
                main.setMessage('#msg', '');
                main.setMessage('#totalTime', '');
                main.setMessage('#calcTime', '');
                main.setMessage('#drawTime', '');
                // get user input as to how close points have to be to be considered the same
                main.TOLERANCE = Options.getTolerance();
                // reset these here because if we just did a reset then they have values right now
                main.TOTAL_CALCULATION_TIME = 0;
                main.TOTAL_DRAW_TIME = 0;
                main.DONE = false;
                main.IS_PROFILING = Options.getProfileOn();
                main.PROFILE_DRAW = Options.getProfileDrawOn();
                if (main.IS_PROFILING)
                {
                    console.profile(fctName);
                }
                main.timeFunction(function () { return main[fctName](); });
                event.preventDefault();
            };
        })(this);
    }
    
    redraw()
    {
        this.LAYERS.redraw();
        this.updateNumberPoints();
        // no need to drawLayers() because cells are always added and never changed
        var timeEnd = performance.now();
        var drawTime = timeEnd - this.TIME_START;
        this.TOTAL_DRAW_TIME += drawTime;
        this.setMessage('#drawTime', 'Draw time: ' + drawTime.toFixed(2) + 'ms current - ' + this.TOTAL_DRAW_TIME.toFixed(2) + 'ms total');
    }
    
    startGrowth()
    {
        this.DONE = false;
        this.CUR_GENERATION = 0;
        if (Options.getAutoGrowthOn())
        {
            this.nextGeneration();
            return false;
        }
        else
        {
            var new_points = this.doGrowth();
            // throw out old points and use new ones
            this.LAYERS.POINTS.setAndCheckPoints(new_points);
            this.DONE = true;
            return true;
        }
    }
    
    doGeneration()
    {
        this.CUR_GENERATION++;
        this.setMessage('#msg', 'Generation ' + this.CUR_GENERATION + ' processing...');
        // grow and then condense
        var new_points = this.doGrowth();
        // don't redraw while setting points because we're going to condense them right away
        this.LAYERS.POINTS.setAndCheckPoints(new_points);
        // condense is quicker than growing when we should have condensed
        this.LAYERS.POINTS.condenseByHull();
        return this.nextGeneration();
    }
    
    nextGeneration()
    {
        var maxGenerations = Options.getGenerations();
        var lastGeneration = !(Options.getAutoGrowthOn() && this.CUR_GENERATION < maxGenerations);
        // show if generation is last, we're showing everything, or we turned the auto toggle off
        var shouldRedraw = Options.getShowEachOn() || lastGeneration;
        if (!lastGeneration)
        {
            // use setTimeout to pass it off because otherwise it doesn't redraw
            setTimeout((function (main)
                        {
                            return function ()
                            {
                                main.timeFunction(function () { return main.doGeneration(); });
                            };
                        })(this),
                        0);
        }
        this.setMessage('#msg', 'Generation ' + this.CUR_GENERATION + ' of ' + maxGenerations + ' complete');
        this.DONE = lastGeneration;
        return shouldRedraw;
    }
    
    initialize()
    {
        this.LAYERS = new Layers();
        this.TOTAL_TIME = 0;
        this.TOTAL_CALCULATION_TIME = 0;
        this.TOTAL_DRAW_TIME = 0;
        this.LAYERS.drawBasemaps();
    }
    
    doRedraw()
    {
        this.LAYERS.draw();
        this.DONE = true;
        return false;
    }
    
    doReset()
    {
        this.initialize();
        this.doRedraw();
        this.LAYERS.POINTS.setAndCheckPoints([new Point(501600, 5715800)]);
        this.DONE = true;
        return true;
    }
    
    doCondense()
    {
        // should never need to check burned cells since points are already in them
        this.LAYERS.POINTS.condenseByHull();
        this.DONE = true;
        return true;
    }
    
    
    updateNumberPoints()
    {
        this.setMessage('#pointCount', '# Points: ' + this.LAYERS.POINTS.array.length);
    }
    
    setMessage(control, msg)
    {
        this.MESSAGES[control] = msg;
    }
    
    showMessages()
    {
        for (var control in this.MESSAGES)
        {
            $(control).text(this.MESSAGES[control]);
        }
        this.MESSAGES = {};
    }
}

function cancelSubmit(fctName)
{
    return MAIN.cancelSubmit(fctName);
}

function load()
{
    MAIN = new Main();
    MAIN.doReset();
    MAIN.redraw();
   
    $('#labels').change(function () { LAYERS.toggleLabels(); });
    $('#grow').click(cancelSubmit('startGrowth'));
    $('#condense').click(cancelSubmit('doCondense'));
    $('#redraw').click(cancelSubmit('doRedraw'));
    $('#reset').click(cancelSubmit('doReset'));
}

$(load);
</script>
    </head>
    <body>
    <div style="margin-top: 2px; margin-left: 2px;">
        <canvas id="lyrOutput" style="z-index: 1; left: 0px; top: 0px;" width="800" height="800">
          <p>This is fallback content for users of assistive technologies or of browsers that don't have full support for the Canvas API.</p>
        </canvas>
        <canvas id="lyrOutCells" style="z-index: 4; position: absolute; left: 2px; top: 2px;" width="800" height="800">
        </canvas>
        <canvas id="lyrActiveCells" style="z-index: 5; position: absolute; left: 2px; top: 2px;" width="800" height="800">
        </canvas>
        <canvas id="lyrPoints" style="z-index: 9; position: absolute; left: 2px; top: 2px;" width="800" height="800">
        </canvas>
        <canvas id="lyrBasemaps" style="z-index: 10; position: absolute; left: 2px; top: 2px;" width="800" height="800">
        </canvas>
    </div>
    <br />
    <br />
    <br />
    <div class="form container col-xs-5" style="width: 530px; position: absolute; padding-top: 10px; padding-left: 0px; padding-right: 0px; margin-top: -858px; margin-left: 810px; margin-right: 0px;">
        <div class="col-xs-12 form-group">
            <span class="inlineinput">
                <div class="col-xs-3 form-group">
                    <input type="checkbox" id="labels" name="labels" checked/>
                    <label for="labels"><span></span>Show Labels</label>
                </div>
                <div class="col-xs-3 form-group">
                    <input type="checkbox" id="profile" name="profile" checked/>
                    <label for="profile"><span></span>Profile CPU</label>
                    <input type="checkbox" id="profileDraw" name="profileDraw" />
                    <label for="profileDraw"><span></span>Include Drawing</label>
                </div>
                <div class="col-xs-3 form-group">
                    <input type="checkbox" id="progress" name="progress" checked/>
                    <label for="progress"><span></span>Show Progress</label>
                </div>
            </span>
        </div>
        <h4>Growth</h4>
        <div class="col-xs-12 form-group">
            <span class="inlineinput">
                <div class="col-xs-3 form-group">
                    <label for="duration">Duration</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="4" type="number" id="duration" name="duration" value="300" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <input type="checkbox" id="autogrow" name="autogrow" checked/>
                    <label for="autogrow"><span></span>Multiple Generations</label>
                    <input type="checkbox" id="showEach" name="showEach"/>
                    <label for="showEach"><span></span>Show Each</label>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="generations">Generations</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="generations" name="generations" value="30" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <input type="checkbox" id="fullHull" name="fullHull" checked/>
                    <label for="fullHull"><span></span>Full Hull First</label>
                </div>
            </span>
        </div>
        <h4>Inputs</h4>
        <div class="col-xs-12 form-group">
            <span class="inlineinput">
                <! -- Defaults pick for C2, WS=15, FFMC = 89, ISI = 8/2, BUI45, ROS=9/1, lb = 2.0 -->
                <div class="col-xs-3 form-group">
                    <label for="rosHead">ROS Head (m/s)</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="rosHead" name="rosHead" value="9" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="rosBack">ROS Back (m/s)</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="rosBack" name="rosBack" value="1" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="lbRatio">LB Ratio</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="lbRatio" name="lbRatio" value="2.0" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="direction">Direction</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="direction" name="direction" value="75" />
                    </div>
                </div>
            </span>
        </div>
        <h4>Options</h4>
        <div class="col-xs-12 form-group">
            <span class="inlineinput">
                <div class="col-xs-3 form-group">
                    <label for="tolerance">Tolerance (m)</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="tolerance" name="tolerance" value="10" /> 
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="numberOfAngles">Directions</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="numberOfAngles" name="numberOfAngles" value="64" />
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="skew">Angle Skew</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="skew" name="skew" value="0.37">
                    </div>
                </div>
                <div class="col-xs-3 form-group">
                    <label for="headAngle">Head Angle</label>
                    <div class="col-xs-12">
                        <input class="input-small form-control" maxlength="3" type="number" id="headAngle" name="headAngle" value="135">
                    </div>
                </div>
            </span>
        </div>
        <div class="col-xs-12 form-group">
            <span class="inlineinput">
                <button style="color: gray" type="submit" id="grow">Grow</button>
                <button style="color: gray" type="submit" id="condense">Condense</button>
                <button style="color: gray" type="submit" id="redraw">Redraw</button>
                <button style="color: gray" type="submit" id="reset">Reset</button>
            </span>
        </div>
        <div class="col-xs-12 form-group">
            <span id="pointCount"></span>
        </div>
        <div class="col-xs-12 form-group">
            <span id="totalTime"></span>
        </div>
        <div class="col-xs-12 form-group">
            <span id="calcTime"></span>
        </div>
        <div class="col-xs-12 form-group">
            <span id="drawTime"></span>
        </div>
        <div class="col-xs-12 form-group">
            <span id="msg"></span>
        </div>
    </div>
    </body>
</html>
