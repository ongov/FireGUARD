check_package <- function(pkg)
{
    if (!(pkg %in% installed.packages()))
    {
        install.packages(pkg)
    }
}

check_package("data.table")
check_package("raster")
check_package("rgdal")
check_package("rgeos")
require(data.table)
require(raster)
require(rgdal)
require(rgeos)

BASE_DIR <- "C:/work/firestarr"
OUTPUT_BASE <- paste0(BASE_DIR, "/../rfiles/")
result <- ""


do_plot <- function(filename, main="", sub="", xlab="Easting", ylab="Northing", proj4=NULL,
                        col=colorRampPalette(c("#ECF7DF", "#FFF550", "#FEEA4E", "#FCDE4B", "#FBD348",
                                                "#FAC846", "#F9BD44", "#F8B241", "#F6A63E", "#F59B3C",
                                                "#F4903A", "#F28437", "#F17934", "#F06E32", "#EF6330",
                                                "#EE582D", "#EC4C2A", "#EB4128", "#EA3626", "#E82A23",
                                                "#E71F20", "#E6141E"))(1000000),
                        add=FALSE)
{
    r <- raster(filename)
    if (!is.null(proj4))
    {
        proj4string(r) <- CRS(proj4)
    }
    if (!is.null(col))
    {
        plot(r,
            main=main,
            sub=sub,
            xlab=xlab,
            ylab=ylab,
            col=col,
            add=add)
    }
    else
    {
        plot(r,
            main=main,
            sub=sub,
            xlab=xlab,
            ylab=ylab,
            add=add)
    }
    return (r)
}

plot_both_test <- function(out_dir, out_file, in_file)
{
}

test_constant <- function(run_dir)
{
    RUN_OUTPUT = paste0(getwd(), "/output/constant/")
    unlink(RUN_OUTPUT, recursive=TRUE)
    dir.create(RUN_OUTPUT, showWarnings=FALSE, recursive=TRUE)
    out_dir = paste0(run_dir, "/constant/")
    unlink(out_dir, recursive=TRUE)
    dir.create(out_dir, showWarnings=FALSE, recursive=TRUE)
    numDays = 1
    slope = 0
    aspect = 0
    for (slope in seq(20, 20, 10))
    {
        for (aspect in seq(0, 315, 45))
        {
            for (wind_speed in seq(10, 10, 5))
            {
                for (wind_direction in seq(0, 315, 45))
                {
                    out_file = sprintf('C2_%03ddays_%03dslp_%03dasp_%03dws_%03dwd',
                                        numDays, slope, aspect, wind_speed, wind_direction)
                    jpeg(filename=paste0(out_dir, out_file, ".jpg"),
                            width=640, height=640)
                    run_constant(RUN_OUTPUT, numDays, slope, aspect, wind_speed, wind_direction)
                    dev.off()
                }
            }
        }
    }
}

find_perim <- function (fire)
{
    perim_dir <- paste0("/work/Test Data/", fire, "/IncidentData/")
    shps <- list.files(perim_dir, pattern=paste0(fire, "_F_2017.....shp$"))
    final_shp <- NULL
    if (0 < length(shps))
    {
        # get final shapefile
        final_shp <- shps[length(shps)]
    }
    else
    {
        # pick last intermediate shapefile
        shps <- list.files(perim_dir, pattern=paste0(fire, "_I_2017.....shp$"))
        if (0 < length(shps))
        {
            final_shp <- shps[length(shps)]
        }
        else
        {
            # pick any shapefile
            shps <- list.files(perim_dir, pattern=paste0(fire, "shp$"))
            if (0 < length(shps))
            {
                final_shp <- shps[length(shps)]
            }
        }
    }
    if (is.null(final_shp))
    {
        return(NULL)
    }
    final_perim <- paste0(perim_dir, final_shp)
    return(final_perim)
}

Con <- function(condition, trueValue, falseValue)
{
    return(condition * trueValue + (!condition) * falseValue)
}

run <- function (fire, day, lat, lon, start_time, out_dir, actualsOnly, final_size=NULL) {
    RUN_OUTPUT = paste0(getwd(), "/output/", fire)
    print(RUN_OUTPUT)
    unlink(RUN_OUTPUT, recursive=TRUE)
    dir.create(RUN_OUTPUT, showWarnings=FALSE, recursive=TRUE)
    dir.create(paste0(getwd(), "/output/", fire), showWarnings=FALSE, recursive=TRUE)
    cmd <- paste0("firestarr.exe ", RUN_OUTPUT, " ",
            day, " ", lat, " ", lon, " ", start_time)
    if (actualsOnly)
    {
        cmd <- paste0(cmd, " -a")
    }
    #~ prob <- paste0(out_dir, "/asc/", fire)
    #~ prob_asc <- paste0(prob, ".asc")
    #~ prob_prj <- paste0(prob, ".prj")
    #~ if (!file.exists(prob_asc))
    #~ {
    print(paste0("Running for ", fire))
    print(cmd)
    result <<- system(cmd, intern=TRUE)
    size <- substr(result[grep("Fire size", result)], 30, 1000)
    proj4 <- substr(result[grep("Projection", result)], 44, 1000)
    pt <- substr(result[grep("Coordinates", result)], 30, 1000)
    utm <- substr(pt, regexpr(" to ", pt)[1] + 4, 1000)
    zone <- as.double(substr(utm, 2, regexpr(", ", utm) - 1))
    s <- substr(utm, regexpr(", ", utm) + 2, 1000)
    easting <- as.double(substr(s, 1, regexpr(", ", s) - 1))
    s <- substr(s, regexpr(", ", s) + 2, 1000)
    northing <- as.double(substr(s, 1, regexpr(")", s) - 1))
    pred_msg <- substr(result[grep("Fire size:", result)], 30, 1000)
    # if ("Fire size: 0.00 - 0.00 ha (expected 0.00 ha)" == size)
    # {
        # print(paste0(fire, " - ", size))
        # print("Can't plot since no results")
        # return()
    # }
    main <- fire
    if (!is.null(final_size))
    {
        main <- sprintf("%s\n%0.0f ha", main, final_size)
    }
    main <- sprintf("%s\nOrigin (%0.3f, %0.3f) converted to (%0.1f, %0.0f, %0.0f)",
                        main, lat, lon, zone, easting, northing)
    shp_utm <- NULL
    final_perim <- find_perim(fire)
    if (!is.null(final_perim))
    {
        print(sprintf("Perimeter file being used is: %s", final_perim))
        shp <- readOGR(final_perim)
        shp_utm <- spTransform(shp, crs(proj4))
    }
    for_what <- 'probability'
    plot_both(fire, out_dir, main, size, proj4, shp_utm, easting, northing, for_what)
}

plot_both <- function(fire, out_dir, main, size, proj4, shp_utm, easting, northing, for_what) {
    # plot to png and screen separately because dev.copy misaligns things
    print(paste0("Plotting ", for_what, " for ", fire))
    vs_raster = paste0('\\', for_what, '_final.asc')
    out_img <- paste0(out_dir, "/", fire, "_", for_what, ".png")
    png(out_img, width=1080, height=1080)
    plot_fire(fire, main, size, proj4, shp_utm, easting, northing, vs_raster)
    dev.off()
    plot_fire(fire, main, size, proj4, shp_utm, easting, northing, vs_raster)
}

plot_fire <- function (fire, main, size, proj4, shp_utm, easting, northing, vs_raster) {
    ext <- extent(raster(paste0('output\\', fire, vs_raster)))
    # figure out largest extent
    if (!is.null(shp_utm))
    {
        ext_shp <- extent(shp_utm)
        ext <- extent(min(ext_shp@xmin, ext@xmin),
                      max(ext_shp@xmax, ext@xmax),
                      min(ext_shp@ymin, ext@ymin),
                      max(ext_shp@ymax, ext@ymax))
    }
    e <- raster(ext)
    e <- setValues(e, 0)
    plot(e, col=NA, legend=FALSE,
            main=main,
            sub=size,
            xlab="Easting",
            ylab="Northing")
    r <- do_plot(paste0('output\\', fire, vs_raster),
            main=main,
            sub=size,
            proj4=proj4,
            add=TRUE)
    if (!is.null(shp_utm))
    {
        plot(shp_utm, border="red", lwd=2, add=TRUE)
    }
    points(easting, northing, pch=19)
}

run_fires <- function(in_file, actualsOnly)
{
    setwd(BASE_DIR)
    run_dir = paste0(OUTPUT_BASE, format(Sys.time(), "%Y-%m-%d_%H%M%S/"))
    unlink(run_dir, recursive=TRUE)
    dir.create(run_dir, showWarnings=FALSE, recursive=TRUE)
    system("make.bat")
    dir.create(paste0(run_dir, 'Data/'), showWarnings=FALSE, recursive=TRUE)
    file.copy('Release/firestarr.exe', run_dir)
    if (file.exists('settings.ini'))
    {
        file.copy('settings.ini', run_dir)
    }
    file.copy('Data/fuel.lut', paste0(run_dir, 'Data/'))
    fires <- as.data.table(read.table(in_file, header=TRUE, sep=","))
    setwd(run_dir)
    cols <- fires[,c("CUR_DIST", "FIRE_NUMBER", "LONGITUDE", "LATITUDE", "START_DATE", "FINAL_SIZE")]
    cols[,`:=`(fire = paste0(CUR_DIST, sprintf("%03d", FIRE_NUMBER)),
                day = substr(START_DATE, 1, 10),
                start_time = substr(START_DATE, 12, 16))]
    out_dir = paste0(getwd(), "/output")
    unlink(out_dir, recursive=TRUE)
    dir.create(out_dir, showWarnings=FALSE, recursive=TRUE)
    #~ fire <- "SLK200"
    #~ day <- "2017-08-27"
    #~ lat <- 52.01
    #~ lon <- -89.024
    #~ start_time <- "12:15"
    #~ final_size = 0
    #~ row <- 1
    for (row in 1:nrow(cols))
    {
        print(sprintf("Processing fire %d of %d", row, nrow(cols)))
        fire <- cols[row, "fire"]
        day <- cols[row, "day"]
        lat <- cols[row, "LATITUDE"]
        lon <- cols[row, "LONGITUDE"]
        start_time <- cols[row, "start_time"]
        final_size <- cols[row, "FINAL_SIZE"]
        run(fire, day, lat, lon, start_time, out_dir, actualsOnly, final_size=final_size)
    }
}

run_constant <- function (out_dir, numDays=1, slope=0, aspect=0, wind_speed=20, wind_direction=180) {
    print(paste0("firestarr.exe test ", out_dir,
                    " ", numDays,
                    " ", slope,
                    " ", aspect,
                    " ", wind_speed,
                    " ", wind_direction
                    ))
    system(paste0("firestarr.exe test ", out_dir,
                    " ", numDays,
                    " ", slope,
                    " ", aspect,
                    " ", wind_speed,
                    " ", wind_direction
                    ));
    do_plot(paste0(out_dir, 'intensity.asc'))
}

showAll <- function()
{
    setwd(BASE_DIR)
    fs = list.files("test/output", pattern="*.asc", recursive = TRUE)
    for (f in fs)
    {
        desc <- sub('.asc', '', f)
        desc <- sub('F002', 'C2', desc)
        desc <- sub('S', 'Slope ', desc)
        desc <- sub('A', 'Aspect ', desc)
        desc <- sub('WD', 'Wind Direction ', desc)
        desc <- sub('WS', 'Wind Speed ', desc)
        desc <- gsub('_', '   ', desc)
        desc <- sub('/', '', f)
        name <- paste0("test/output/", f)
        print(name)
        
        if (sub("source", "", f) != f)
        {
            do_plot(name, col=NULL)
        }
        else
        {
            do_plot(name, desc)
        }
    }
}

in_file <- "../FireSTARR Test data.csv"
actualsOnly <- TRUE
setwd(BASE_DIR)
run_fires(in_file, actualsOnly)
