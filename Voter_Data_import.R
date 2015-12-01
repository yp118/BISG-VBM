# Loading necessary libraries
library(dplyr)

# Setting working directory
setwd("C:/Users/Yogi/Desktop/2014 Data Extracted")

# Creating Voting history dataframe by loading first voting sheet
VoteHistory.2014 <- read.csv("Master_Voting_History_List_ Part1_11_26_2014_11_32_00.txt")

# Looping through text documents and reading into R
for (i in 2:32) {
  # Create file name
  sheetname <- paste("Master_Voting_History_List_ Part",i,"_11_26_2014_11_32_00.txt", sep = "")
  # Load file in as dataframe
  sheet <- read.csv(sheetname)
  # Attach rows from file to master voter history dataframe 
  VoteHistory.2014 <- rbind(VoteHistory.2014, sheet)
}

# Creating Voter information dataframe by loading first information sheet
VoterInfo.2014 <- read.csv("Master_Voting_History_List_Voter_Details_ Part1_11_26_2014_11_31_00.txt")

# Looping through text documents and reading into R
for (i in 2:29) {
  # Create file name
  sheetname <- paste("Master_Voting_History_List_Voter_Details_ Part",i,"_11_26_2014_11_31_00.txt", sep = "")
  # Load file in as dataframe
  sheet <- read.csv(sheetname)
  # Attach rows from file to master voter information dataframe
  VoterInfo.2014 <- rbind(VoterInfo.2014, sheet)
}
rm(sheetname, i, sheet)

# Converting to dplyr tbls
Votes.2014 <- tbl_df(VoteHistory.2014)
Info.2014 <- tbl_df(VoterInfo.2014)

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