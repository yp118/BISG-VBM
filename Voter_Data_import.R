# Loading necessart libraries
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
for (i in 2:32) {
  # Create file name
  sheetname <- paste("Master_Voting_History_List_Voter_Details_ Part",i,"_11_26_2014_11_31_00.txt", sep = "")
  # Load file in as dataframe
  sheet <- read.csv(sheetname)
  # Attach rows from file to master voter information dataframe
  VoterInfo.2014 <- rbind(VoterInfo.2014, sheet)
}

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

inner_join(Votes.2014, Info.2014, by = "VOTER_ID")
