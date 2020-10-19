#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(data.table)
options(rgl.useNULL = TRUE)
library(rgl)
library(DT)
library(dplyr)
library(shinycssloaders)

fuel <- fread('fuel.csv')
duff <- fread('duff.csv')

FUELS <- c('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'D1_D2', 'M1_M2', 'M3_M4', 'S1', 'S2', 'S3')

probabilityPeat <- function(fuel_name, mc_fraction)
{
  f <- fuel[fuel == fuel_name]
  # Anderson table 1
  Pb <- f$Pb
  # Anderson table 1
  Fi <- f$Fi
  Pi <- Fi * Pb
  # inorganic ratio
  Ri = Fi / (1 - Fi)
  const_part <- -19.329 + 1.7170 * Ri + 23.059 * Pi
  # Anderson eq 1
  return(1 / (1 + exp(17.047 * mc_fraction / (1 - Fi) + const_part)))
}


# \brief Ignition Probability (% / 100) [eq Ig-1]
# \param mc_pct Moisture content, percentage dry oven weight
# \return Ignition Probability (% / 100) [eq Ig-1]
duffFunction <- function(duff_name, mc_pct)
{
  f <- duff[type == duff_name]
  ConstantPart <- f$B0 + f$B2 * f$Ash + f$B3 * f$Rho
  d <- 1 + exp(-(f$B1 * mc_pct + ConstantPart))
  if (0 == d)
  {
    return(1.0)
  }
  return(1.0 / d)
}


# \brief Survival probability calculated using probability of ony survival based on multiple formulae
# \param wx FwiWeather to calculate survival probability for
# \return Chance of survival (% / 100)

survivalProbability <- function(fuel_name, ffmc, dmc)
{
  DUFF_FFMC_DEPTH <- 1.2
  f <- fuel[fuel == fuel_name]
  # divide by 100 since we need moisture ratio
  #    IFERROR(((1 / (1 + EXP($G$43 + $I$43 *
  #            (mcFfmc * $O$43 + $N$43)))) -
  #            (1 / (1 + EXP($G$43 + $I$43 * (2.5 * $O$43 + $N$43)))))
  #            / (1 / (1 + EXP($G$43 + $I$43 * $N$43))), 0)
  # HACK: use same constants for all fuels because they seem to work nicer than
  # using the ratios but they change anyway because of the other fuel attributes
  WFfmc <- 0.25
  WDmc <- 1.0
  RatioHartford <- 0.5
  RatioFrandsen <- 1.0 - RatioHartford
  RatioAspen <- 0.5
  RatioFuel <- 1.0 - RatioAspen
  
  mcFfmcPct <- 147.2 * (101 - ffmc) / (59.5 + ffmc)
  mcFfmc <- mcFfmcPct / 100
  mcDmcPct <- exp((dmc - 244.72) / -43.43) + 20
  mcDmc <- mcDmcPct / 100
  
  dmcRatio <- (f$duff - DUFF_FFMC_DEPTH) / f$duff;
  ffmcRatio <- 1 - dmcRatio
  
  mc_ffmc <- mcFfmc * WFfmc + WDmc
  McFfmcSaturated <- 2.5 * WFfmc + WDmc
  McDmc <- WDmc
  prob_ffmc_peat <- probabilityPeat(fuel_name, mc_ffmc)
  prob_ffmc_peat_saturated <- probabilityPeat(fuel_name, McFfmcSaturated)
  prob_ffmc_peat_zero <- probabilityPeat(fuel_name, McDmc)
  prob_ffmc_peat_weighted <- (prob_ffmc_peat - prob_ffmc_peat_saturated) / prob_ffmc_peat_zero
  prob_ffmc <- duffFunction(f$FFMC, mc_ffmc * 100)
  prob_ffmc_saturated <- duffFunction(f$FFMC, McFfmcSaturated * 100)
  prob_ffmc_zero <- duffFunction(f$FFMC, McDmc)
  prob_ffmc_weighted <- (prob_ffmc - prob_ffmc_saturated) / prob_ffmc_zero
  term_otway <- exp(-3.11 + 0.12 * dmc)
  # HACK: spreadsheet is doing this, which would be so that DMC 0 => prob survival 0
  #~ prob_otway <- (term_otway - exp(-3.11)) / (1 + term_otway)
  # this seems more correct than trying to make that adjustment
  prob_otway <- term_otway / (1 + term_otway)
  mc_pct <- (mcDmcPct * dmcRatio + mcFfmcPct * ffmcRatio)
  prob_weight_ffmc <- duffFunction(f$FFMC, mc_pct)
  prob_weight_ffmc_peat <- probabilityPeat(fuel_name, mc_pct / 100)
  prob_weight_dmc <- duffFunction(f$DMC, mcDmcPct)
  prob_weight_dmc_peat <- probabilityPeat(fuel_name, mcDmc)
  for_what <- paste0(fuel_name, ' ', ffmc, ', ', dmc)
  #print(for_what)
  stopifnot(prob_ffmc_peat <= 1)
  stopifnot(prob_ffmc_peat_saturated <= 1)
  stopifnot(prob_ffmc_peat_zero <= 1)
  stopifnot(prob_ffmc_peat_weighted <= 1)
  stopifnot(prob_ffmc <= 1)
  stopifnot(prob_ffmc_saturated <= 1)
  stopifnot(prob_ffmc_zero <= 1)
  stopifnot(prob_ffmc_weighted <= 1)
  stopifnot(prob_otway <= 1)
  stopifnot(prob_weight_ffmc <= 1)
  stopifnot(prob_weight_ffmc_peat <= 1)
  stopifnot(prob_weight_dmc <= 1)
  stopifnot(prob_weight_dmc_peat <= 1)
  #~ =1 -
  #~ (1 - ((1 / (1 + EXP($G$43 + $I$43 * mc_ffmc))) - (1 / (1 + EXP($G$43 + $I$43 * McFfmcSaturated)))) / (1 / (1 + EXP($G$43 + $I$43 * WDmc)))) *
  #~ (1 - (((1 / (1 + EXP(-($AC$42 + $AD$42 * mc_ffmc)))) - (1 / (1 + EXP(-($AC$42 + $AD$42 * McFfmcSaturated))))) / (1 / (1 + EXP(-($AC$42 + $AD$42 * WDmc)))))) *
  #~ (
  #~ (1 - ((EXP($L$44 + $M$44 * dmc) - (EXP($L$44)))/(1 + EXP($L$44 + $M$44 * dmc)))) * RatioAspen +
  #~ ((1 - (1/(1+EXP(-($AC$42 + $AD$42 * (mcDmc * $N$42 + mcFfmc * $O$42)))))) * RatioFrandsen +
  #~ (1 - (1 / (1 + EXP($G$43 + $I$43 * (mcDmc * $N$42 + mcFfmc * $O$42))))) * RatioHartford) *
  #~ ((1 - (1 / (1+EXP(-($AC$43 + $AD$43 * mcDmc))))) * RatioFrandsen +
  #~ (1 - (1 / (1 + EXP($G$43 + $I$43 * mcDmc)))) * RatioHartford)
  #~ * RatioFuel
  #~ )
  # chance of survival is 1 - chance of it not surviving in every fuel
  tot_prob <- 1 - (1 - prob_ffmc_peat_weighted) * (1 - prob_ffmc_weighted) * (
    (1 - prob_otway) * RatioAspen +
      ((1 - prob_weight_ffmc_peat) * RatioHartford
       + (1 - prob_weight_ffmc) * RatioFrandsen) *
      ((1 - prob_weight_dmc_peat) * RatioHartford
       + (1 - prob_weight_dmc) * RatioFrandsen)
    * RatioFuel)
  return(tot_prob)
}


# Define UI for application that draws a histogram
ui <- fluidPage(
  
  # Application title
  titlePanel("Fire Survival Probability"),
  # Show a plot of the generated distribution
  tabsetPanel(id='fuelName',
              tabPanel("3d"),
              tabPanel("Survival"),
              tabPanel("C1"),
              tabPanel("C2"),
              tabPanel("C3"),
              tabPanel("C4"),
              tabPanel("C5"),
              tabPanel("C6"),
              tabPanel("C7"),
              tabPanel("D1_D2"),
              tabPanel("M1_M2"),
              tabPanel("M3_M4"),
              tabPanel("S1"),
              tabPanel("S2"),
              tabPanel("S3"),
              mainPanel(
                flowLayout(
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C1'",
                                   rglwidgetOutput("c1Plot") %>% withSpinner(color="#0dc5c1")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C2'",
                                   rglwidgetOutput("c2Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C3'",
                                   rglwidgetOutput("c3Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C4'",
                                   rglwidgetOutput("c4Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C5'",
                                   rglwidgetOutput("c5Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C6'",
                                   rglwidgetOutput("c6Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'C7'",
                                   rglwidgetOutput("c7Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'D1_D2'",
                                   rglwidgetOutput("d1d2Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'M1_M2'",
                                   rglwidgetOutput("m1m2Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'M3_M4'",
                                   rglwidgetOutput("m3m4Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'S1'",
                                   rglwidgetOutput("s1Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'S2'",
                                   rglwidgetOutput("s2Plot")),
                  conditionalPanel("input.fuelName == '3d' || input.fuelName == 'S3'",
                                   rglwidgetOutput("s3Plot")),
                  cellArgs=list(style='position: relative; float: left; width: 520px;')
                ),
                conditionalPanel("input.fuelName != '3d' && input.fuelName != 'Survival'",
                                 fluidRow(column(6, plotOutput("ffmcPlot")),
                                          column(6, plotOutput("dmcPlot"))),
                                 DT::dataTableOutput("survivalTable")
                ),
                conditionalPanel("input.fuelName == 'Survival'",
                                 fluidRow(column(6, plotOutput("ffmcSurvivalMin")),
                                          column(6, plotOutput("dmcSurvivalMin"))),
                                 fluidRow(column(6, plotOutput("ffmcSurvivalMean")),
                                          column(6, plotOutput("dmcSurvivalMean"))),
                                 fluidRow(column(6, plotOutput("ffmcSurvivalMax")),
                                          column(6, plotOutput("dmcSurvivalMax")))
                ),
                width='100%'
              )
  )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
  getTable <- reactive(function(fuel_name)
  {
    dmc <- seq(0, 101, 1)
    ffmc <- seq(0, 101,1)
    f <- function(dmc, ffmc) { survivalProbability(fuel_name, ffmc, dmc) }
    p <- outer(dmc, ffmc, f)
    p[is.na(p)] <- 1
    df <- data.table(p)
    n <- sapply(as.character(seq(0, 101)), function(x){paste0('FFMC_', x)},  USE.NAMES=FALSE)
    names(df) <- n
    df$dmc <- as.integer(dmc)
    cols <- c('dmc', n)
    df <- df[, ..cols]
    df
  })
  
  TABLES <- reactive(list(
    C1=(getTable()('C1')),
    C2=(getTable()('C2')),
    C3=(getTable()('C3')),
    C4=(getTable()('C4')),
    C5=(getTable()('C5')),
    C6=(getTable()('C6')),
    C7=(getTable()('C7')),
    D1_D2=(getTable()('D1_D2')),
    M1_M2=(getTable()('M1_M2')),
    M3_M4=(getTable()('M3_M4')),
    S1=(getTable()('S1')),
    S2=(getTable()('S2')),
    S3=(getTable()('S3'))
  ))
  
  render3d <- function(fuel_name)
  {
    renderRglwidget({
      dmc <- seq(0, 101, 1)
      ffmc <- seq(0, 101,1)
      f <- function(dmc, ffmc) { survivalProbability(fuel_name, ffmc, dmc) }
      p <- outer(dmc, ffmc, f)
      p[is.na(p)] <- 1
      persp3d(x=dmc, y=ffmc, z=p, main=fuel_name, ticktype='detailed', col=seq(1, 7))
      bg3d('white')
      view3d(userMatrix=rotationMatrix(-60*pi/180, 1, -0.5, -1))
      rglwidget()
    })
  }
  
  output$c1Plot <- render3d('C1')
  output$c2Plot <- render3d('C2')
  output$c3Plot <- render3d('C3')
  output$c4Plot <- render3d('C4')
  output$c5Plot <- render3d('C5')
  output$c6Plot <- render3d('C6')
  output$c7Plot <- render3d('C7')
  output$d1d2Plot <- render3d('D1_D2')
  output$m1m2Plot <- render3d('M1_M2')
  output$m3m4Plot <- render3d('M3_M4')
  output$s1Plot <- render3d('S1')
  output$s2Plot <- render3d('S2')
  output$s3Plot <- render3d('S3')
  
  output$ffmcPlot <- renderPlot({
    fuel_name <- input$fuelName
    t <- TABLES()
    df <- tryCatch({t[[fuel_name]]}, error=NULL)
    if (is.null(df))
    {
      return()
    }
    means <- as.double(df[,-c('dmc')][, lapply(.SD, mean)])
    mins <- as.double(df[,-c('dmc')][, lapply(.SD, min)])
    maxs <- as.double(df[,-c('dmc')][, lapply(.SD, max)])
    FFMC <- seq(0, 101)
    plot(means ~ FFMC, type='l', ylim=c(0, 1), ylab='Survival Probability', main='FFMC vs Survival Probability', col='orange')
    lines(mins, col='blue')
    lines(maxs, col='grey')
  })
  
  makeFfmcSurvival <- function(fct, name)
  {
    renderPlot({
      t <- TABLES()
      df <- NULL
      for (fuel_name in FUELS)
      {
        cur <- tryCatch({t[[fuel_name]]}, error=NULL)
        if (!is.null(cur))
        {
          cur <- copy(cur)
          cur$fuelName <- fuel_name
          df <- rbind(df, cur)
        }
      }
      means <- df[,-c('dmc')][, lapply(.SD, fct), by=c('fuelName')]
      FFMC <- seq(0, 101)
      for (fuel_name in FUELS)
      {
        f <- as.double(means[fuelName == fuel_name][, -c('fuelName')])
        colour <- which(FUELS == fuel_name)
        if (fuel_name == 'C1')
        {
          plot(f ~ FFMC, type='l', ylim=c(0, 1), ylab=paste0(name, ' Probability'), main='FFMC vs Survival Probability', col=colour)
        }
        else
        {
          lines(f ~ FFMC, col=colour)
        }
      }
      legend("topleft", legend=FUELS, col=seq(1, length(FUELS)), lty=1, ncol=2, cex=0.75)
    })
  }
  
  output$ffmcSurvivalMin <- makeFfmcSurvival(min, 'Minimum')
  output$ffmcSurvivalMean <- makeFfmcSurvival(mean, 'Average')
  output$ffmcSurvivalMax <- makeFfmcSurvival(max, 'Maximum')
  
  output$dmcPlot <- renderPlot({
    fuel_name <- input$fuelName
    t <- TABLES()
    df <- tryCatch({t[[fuel_name]]}, error=NULL)
    if (is.null(df))
    {
      return()
    }
    df <- transpose(df)
    # get rid of dmc row
    df <- df[2:nrow(df),]
    n <- sapply(as.character(seq(0, 101)), function(x){paste0('DMC_', x)},  USE.NAMES=FALSE)
    names(df) <- n
    df$ffmc <- as.integer(seq(0, 101))
    cols <- c('ffmc', n)
    df <- df[, ..cols]
    means <- as.double(df[,-c('ffmc')][, lapply(.SD, mean)])
    mins <- as.double(df[,-c('ffmc')][, lapply(.SD, min)])
    maxs <- as.double(df[,-c('ffmc')][, lapply(.SD, max)])
    DMC <- seq(0, 101)
    plot(means ~ DMC, type='l', ylim=c(0, 1), ylab='Survival Probability', main='DMC vs Survival Probability', col='orange')
    lines(mins, col='blue')
    lines(maxs, col='grey')
  })
  
  makeDmcSurvival <- function(fct, name)
  {
    renderPlot({
      t <- TABLES()
      df <- NULL
      for (fuel_name in FUELS)
      {
        cur <- tryCatch({t[[fuel_name]]}, error=NULL)
        if (!is.null(cur))
        {
          cur <- transpose(cur)
          # get rid of dmc row
          cur <- cur[2:nrow(cur),]
          n <- sapply(as.character(seq(0, 101)), function(x){paste0('DMC_', x)},  USE.NAMES=FALSE)
          names(cur) <- n
          cur$ffmc <- as.integer(seq(0, 101))
          cols <- c('ffmc', n)
          cur <- cur[, ..cols]
          cur$fuelName <- fuel_name
          df <- rbind(df, cur)
        }
      }
      
      
      means <- df[,-c('ffmc')][, lapply(.SD, fct), by=c('fuelName')]
      DMC <- seq(0, 101)
      for (fuel_name in FUELS)
      {
        f <- as.double(means[fuelName == fuel_name][, -c('fuelName')])
        colour <- which(FUELS == fuel_name)
        if (fuel_name == 'C1')
        {
          plot(f ~ DMC, type='l', ylim=c(0, 1), ylab=paste0(name, ' Probability'), main='DMC vs Survival Probability', col=colour)
        }
        else
        {
          lines(f ~ DMC, col=colour)
        }
      }
      legend("topleft", legend=FUELS, col=seq(1, length(FUELS)), lty=1, ncol=2, cex=0.75)
    })
  }
  
  output$dmcSurvivalMin <- makeDmcSurvival(min, 'Minimum')
  output$dmcSurvivalMean <- makeDmcSurvival(mean, 'Average')
  output$dmcSurvivalMax <- makeDmcSurvival(max, 'Maximum')
  
  
  output$survivalTable <- DT::renderDataTable(DT::datatable({
    TABLES()[[input$fuelName]]
  }))
}

# Run the application 
shinyApp(ui = ui, server = server)
