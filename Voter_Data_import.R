# Loading necessary libraries
library(dplyr)

# Setting working directory
setwd("C:/Users/Yogi/Desktop/2014 Data Extracted")

# Creating Voting history dataframe by loading first voting sheet
Votes.2014 <- read.csv("Master_Voting_History_List_ Part1_11_26_2014_11_32_00.txt") 

# Looping through text documents and reading into R
for (i in 2:32) {
  Votes.2014 <-
    paste("Master_Voting_History_List_ Part",i,"_11_26_2014_11_32_00.txt", sep = "") %>%
    read.csv() %>% 
    rbind(Votes.2014)
}

# Load and add 2012 data not included in 2014 CD
root <- "C:/Users/Yogi/Desktop/2012 Data Extracted/"
for (i in 1:27) {
  Votes.2014 <-
  paste(root, "Master_Voting_History_List_ Part", i ,"_12_10_2012_16_23_00.txt", sep = "") %>%
    read.csv() %>% 
    anti_join(Votes.2014, by = "VOTER_ID") %>%
    rbind(Votes.2014)
}

# Creating Voter information dataframe by loading first information sheet
Info.2014 <- read.csv("Master_Voting_History_List_Voter_Details_ Part1_11_26_2014_11_31_00.txt") %>% tbl_df()

# Looping through text documents and reading into R
for (i in 2:29) {
  Info.2014 <-
  paste("Master_Voting_History_List_Voter_Details_ Part",i,"_11_26_2014_11_31_00.txt", sep = "") %>%
  read.csv() %>%
  rbind(Info.2014)
}

# Load and add 2012 data not included in 2014 CD
for (i in 1:26) {
  Info.2014 <-
  paste(root, "Master_Voting_History_List_Voter_Details_ Part", i ,"_12_10_2012_16_23_00.txt", sep = "") %>%
    read.csv() %>% 
    anti_join(Info.2014, by = "VOTER_ID") %>%
    rbind(Info.2014)  
}

rm(i)

# Getting list of unique vote ID's from both datasets
Votes.IDs <- Votes.2014 %>%
  select(VOTER_ID) %>%
  arrange(VOTER_ID) %>%
  distinct()

Info.IDs <- Info.2014 %>%
  select(VOTER_ID) %>%
  arrange(VOTER_ID) %>%
  distinct()

Votes.IDs
Info.IDs

# Calculating total number of unmatched Voter Ids
a <- setdiff(Votes.IDs, Info.IDs)
b <- setdiff(Info.IDs, Votes.IDs)
c <- bind_rows(a,b)
count(distinct(c))


# Creating tables for umatched votes
unmatched_Info <- filter(Info.2014, VOTER_ID %in% b$VOTER_ID)
unmatched_Votes <- filter(Votes.2014, VOTER_ID %in% a$VOTER_ID)


# Checking which counties unmatched votes are coming from. 
unmatched_Info %>%
  select(COUNTY) %>%
  distinct()
unmatched_Votes %>%
  select(COUNTY_NAME) %>%
  distinct()

unmatched_Votes
unmatched_Info


intersect(Votes.IDs, Info.OldIDs)

setdiff(Info.OldIDs, Votes.IDs)
c <- bind_rows(a,b)
count(distinct(c))