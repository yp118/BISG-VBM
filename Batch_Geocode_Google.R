library(stringr)
library(RJSONIO)
library(RCurl)
options(stringsAsFactors=F)

setwd("")

data <- read.csv("", header=T)
data$ZIP <- str_pad(data$zip, 5, pad = "0")
x <- cbind(data$, data$, data$, data$)
data$inName <- apply(x,1,paste,collapse=" ")

###

construct.geocode.url <- function(address, return.call = "json", sensor = "false") {
  root <- "https://maps.google.com/maps/api/geocode/"
  u <- paste(root, return.call, "?address=", address, "&sensor=", sensor, sep = "")
  return(URLencode(u))
}

GeoCode <- function(address,verbose=FALSE) {
  if(verbose) cat(address,"\n")
  u <- construct.geocode.url(address)
  doc <- getURL(u, ssl.verifypeer = FALSE)
  x <- fromJSON(doc,simplify = FALSE)
  lat <- x$results[[1]]$geometry$location$lat
  lng <- x$results[[1]]$geometry$location$lng
  status <- x$status
  level <- x$results[[1]]$types
  namefound <- x$results[[1]]$formatted_address
  multipleXY = "N"
  if (length(lng)>1 ){ multipleXY = "Y" }
  return(list(status = status, levels=level, lat= lat[1], lng= lng[1], multipleXY= multipleXY, namefound = namefound)) 
}


######################################################
###############GEOCODE ADDRESSES######################
######################################################

 = c(data$inName)

results = data.frame(data, namefound = "NA", status="NA",level="NA",lat=NA,lon=NA, problem=factor("N", levels=c("Y","N")), stringsAsFactors=F)
for (i in 1:length(loc_in)){
  loc_in[i] <- gsub("#", "", loc_in[i])
  result = as.data.frame(googGeoCode(loc_in[i]))
  print(result)
  results[i,] = c(data[i,],as.character(result[,6]),as.character(result[,c(1)]),as.character(result[,c(2)]),result[,c(3,4)],as.character(result[,5]))
  Sys.sleep(2)
}

for (i in i:length(data$inName)) {
  print(data$inName[i])  
  
} 

write.csv(results, file = "results2.csv")


