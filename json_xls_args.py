
import os
import subprocess
import sys
import logging
import argparse
import re
import string
import xlwt
from subprocess import check_output

#########################################################################################
class tweetAnalysis(object):
    """
    Main functional class 
    """
    #--------------------------------------------
    
    def __init__(self, **kwargs):
        self.listId = []
        self.listName = []
        self.loadInpFile = {}
        self.loaddictionary = []
        self.scores = dict()
     
    def parse_args(self, args):
        """Parse the command-line arguments."""
        global cmdArgs
        p = argparse.ArgumentParser(prog='repoquery_hosts')
        
        p.add_argument('-inp', '--input', action='store',  dest='inp',  default="json_files",
                       help="Provide input DIR wrto /Python27/Lib")
        
        p.add_argument('--verbose',  action='store',  dest='verbosity',  default="INFO",
                       help="Provide verbosity level for logging")  

        cmdArgs = p.parse_args(args)
        #print("cmdArgs is ", cmdArgs, "\n")

    def create_dictionary(self):
        self.loaddictionary = open('./sent_dict.txt', 'r')
        for line in self.loaddictionary:
            if re.match(r'^[a-z]', line):
                term, score = line.split('\t')
                #print(" Term and score %s & %s" %(term,score))
                self.scores[term] = float(score)
        self.loaddictionary.close() 
        
                              
    
    def parse_files(self):
        all_files = check_output(["dir", "/b", cmdArgs.inp], shell=True)
        split_files = all_files.split('\n')
        for one_file in split_files:
            one_file.rstrip()
            print("one_file is %s" %one_file)
            if re.match(r'^[a-z]', one_file):  #parse out files that start with [a-z]
                self.loadInpFile = one_file
                file_name = self.loadInpFile.split('.')
                #print("file_name is %s" %file_name[0])
                self.parse_tweets(file_name[0])


    def parse_tweets(self, file_name):
        """Parse the tweets into excel sheets."""

        #-------------------------------------------
        ## Store the regexps for matching
        created_pat   = re.compile(r'{"created_at":', re.VERBOSE)
        id_pat        = re.compile(r'^\s*"id":', re.VERBOSE)
        text_pat      = re.compile(r'^\s*"text":', re.VERBOSE)
        name_pat      = re.compile(r'^\s*"name":', re.VERBOSE)
        followers_pat = re.compile(r'^\s*"followers_count":', re.VERBOSE)
        friends_pat   = re.compile(r'^\s*"friends_count":', re.VERBOSE)
        timezone_pat  = re.compile(r'^\s*"time_zone":', re.VERBOSE)
        retweet_pat   = re.compile(r'"retweet_count":', re.VERBOSE)
        lang_pat      = re.compile(r'^\s*"lang":"[a-z]*"}', re.VERBOSE)
        
        
        print(" ... file_name is %s" %file_name)

        self.loadInpFile = "".join(["./", cmdArgs.inp, "/", file_name, ".json"])
        lines     = open(self.loadInpFile, 'r')

        outfile   = open('./tweets_text.txt', 'a')

        #update excel sheet
        book = xlwt.Workbook()
        sheet1 = book.add_sheet("Sindhuri_1")

        sheet1.write(0, 0, "ID Number")
        sheet1.write(0, 1, "Text and hashtag")
        sheet1.write(0, 2, "Sentiment score")
        sheet1.write(0, 3, "User Name")
        sheet1.write(0, 4, "Followers Count")
        sheet1.write(0, 5, "Friends Count")
        sheet1.write(0, 6, "User TimeZone")
        sheet1.write(0, 7, "Retweet Count")
        
        row = 0
        #col = 0 #id_pat takes care of this
        
        for line in lines:
            #print("Line is %s" %line)
            lineSplit = line.split(',')
            
            for lineSp in lineSplit:
                #print("%s" %lineSp)
                #id_match = re.match(id_pat, lineSp)
                if created_pat.search(lineSp):
                    #print >>outfile, ("\nFound created_pat %s" %lineSp)
                    continue
                elif id_pat.match(lineSp):
                    #print >>outfile, ("ID line : %s" %lineSp)
                    actual_id = lineSp.split(':')
                    
                    row += 1
                    col = 0
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_id[1]))
                    sheet1.write(row, col, actual_id[1])
                    col += 1
                    continue
                elif text_pat.match(lineSp):
                    #print >>outfile, ("TEXT line : %s" %lineSp)
                    actual_text = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_text[1]))
                    tweet = actual_text[1]
                    split_words = tweet.split()
                    #print ("RAJA split_words is %s" %split_words)
                    total_score = 0
                    for each_word in split_words:
                        #print("RAJA each_word is %s" %each_word)
                        if each_word in self.scores:
                            this_wordscore = self.scores[each_word]
                            #print("each word and score %s & %s" %(each_word,this_wordscore))
                            total_score += this_wordscore
                    #if total_score > 0 :
                        #print("text and score %s & %s" %(actual_text[1],total_score))
                    sheet1.write(row, col, actual_text[1])
                    col +=1
                    sheet1.write(row, col, total_score)
                    col +=1
                    continue
                elif name_pat.match(lineSp):
                    #print >>outfile, ("NAME line : %s" %lineSp)
                    actual_name = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_name[1]))
                    temp_name = actual_name[1].lstrip('"')
                    temp_name = temp_name.rstrip('"')
                    sheet1.write(row, col, temp_name)
                    col += 1
                    continue
                elif followers_pat.match(lineSp):
                    #print >>outfile, ("FOLLOWERS line : %s" %lineSp)
                    actual_follower = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_follower[1]))
                    sheet1.write(row, col, actual_follower[1])
                    col += 1
                    continue
                elif friends_pat.match(lineSp):
                    #print >>outfile, ("FRIENDS line : %s" %lineSp)
                    actual_friend = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_friend[1]))
                    sheet1.write(row, col, actual_friend[1])
                    col += 1
                    continue
                elif timezone_pat.match(lineSp):
                    #print >>outfile, ("TIMEZONE line : %s" %lineSp)
                    actual_timezone = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_timezone[1]))
                    #actual_timezone[1] = actual_timezone[1].lstrip('"')
                    #actual_timezone[1] = actual_timezone[1].rstrip('"')
                    sheet1.write(row, col, actual_timezone[1])
                    col += 1
                    continue
                elif retweet_pat.match(lineSp):
                    #print ("RETWEET line : %s" %lineSp)
                    actual_retweet = lineSp.split(':')
                    #print >>outfile, ("row:%s col:%s %s" %(row, col, actual_retweet[1]))
                    sheet1.write(row, col, actual_retweet[1])
                    col += 1
                    continue
                elif lang_pat.match(lineSp):
                    #col = 0
                    #print >>outfile, ("Found next 'created_at' line, BREAK : %s\n\n" %lineSp)
                    break
            if(row%5000 == 0):
                print("Completed %s tweets ..\n" %row)

        print("Read all the tweets!! \n")  
        loadOutFile = "".join(["./", cmdArgs.inp, "/", file_name, ".xls"])
        book.save(loadOutFile)
      

#########################################################################################    
##---MAIN----##
if __name__ == '__main__':

   #For Normal completion
   exitCode = 0

   try:
     print 'Executing json to csv ..\n'
     diffHosts = tweetAnalysis()
     diffHosts.parse_args(sys.argv[1:])
     diffHosts.create_dictionary()
     diffHosts.parse_files()
      
   except KeyboardInterrupt:
      Log.fatal("Saw KeyboardInterrupt.")

   print("\n.. Exit Program.")
   sys.exit(exitCode)
