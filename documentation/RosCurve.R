library(cffdrs)
#~ library(data.table)
#~ library(dplyr)
#~ data("test_fbp")
#~ df <- test_fbp

df <- data.frame(FFMC=seq(0, 1010) / 10)
df[,"FuelType"] <- "C2"
df[,"LAT"] <- 48.970082
df[,"LONG"] <- -93.7019721
df[,"ELV"] <- 100
df[,"BUI"] <- 70
df[,"WS"] <- 20.0
df[,"WD"] <- 0
df[,"GS"] <- 50
df[,"Dj"] <- 180
df[,"D0"] <- NA
df[,"hr"] <- 1.0
df[,"PC"] <- NA
df[,"PDF"] <- NA
df[,"GFL"] <- NA
df[,"cc"] <- NA
df[,"theta"] <- 0
df[,"Accel"] <- 0
df[,"Aspect"] <- 0


f <- sort(fbp(df)[,"ROS"])
r = data.frame(FFMC=sort(df[,"FFMC"]), ROS=f)
#~ r <- merge(df, f, all.x=TRUE)[,c("FFMC", "ROS")]
write.table(r, "C:/FireGUARD/documentation/ros.csv", sep=",", row.names=FALSE)

#~ ffmc <- read.csv('C:/Users/evensjo/OneDrive - Government of Ontario/work/fban/testFARduration/ffmc_pm.csv')

#~ ffmcs <- t(ffmc[ffmc[,"LST"] %in% c(1500, 1700),])

#~ peak <- merge(ffmc, r, by.x=c("X1700"), by.y=c("FFMC"), all.x=TRUE)[,c("FFMC", "X1700", "X1500", "ROS")]

#~ at_1500 <- merge(ffmc, r, by.x=c("X1500"), by.y=c("FFMC"), allow.cartesian=TRUE)

#~ j <- merge(peak, r, by.x=c("X1500"), by.y=c("FFMC"), all.x=TRUE)
