# Example of calling Python app from Perforce custom tools
# python -u "c:\Pushout2\P4_SciptLabel.py" %a $r

import sys
import subprocess
from subprocess import Popen
import re

def main(argv):

    # print 'Number of arguments:', len(sys.argv), '.'
    # print 'Argument list:', str(sys.argv)
    if len(sys.argv)<2:
        sys.exit(1)

    if not "PnL-" in sys.argv[1]:
        print 'Please call as: python -u "c:\Pushout2\P4_SciptLabel.py" %a $r'
        sys.exit(1)

    label = sys.argv[1]
    print label


    print 'Getting File Descriptions for label "' + label + '"'
    recordset = execSQL(label)
    print recordset

    # parse and save
    print 'Parsing the strings'
    jlist = parseRecordset(recordset)

    print 'Saving the file'
    saveFile (jlist, label)

    print '------ Operation completed. ------1'
    sys.exit()




#########
## SQL
#########
def execSQL(label):

    p4sqlLocation = "C:\\Program Files (x86)\\Perforce\\P4Report\\p4sql"
    p4root = "//reReporting/mainline/Projects/PNL/009_GR0000_v7_SQL2008Migration/"
    sqlString = "SELECT 'D' as D, f.Revision, c.Date as SubmitionDate, c.User, REPLACE(REPLACE(c.Description,CHAR(13),' '),CHAR(10),' ') as Descr, f.File FROM Files f INNER JOIN Changes c on f.Change = c.Change WHERE f.RevSpec = '" + label + "' and p4options = 'longdesc';"
    execString = "\"" + p4sqlLocation + "\"" + " -q -s" + "\"" + sqlString + "\""

    #print execString
    p = subprocess.Popen (execString, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    return out



###############################
##  Parse |-delimited data
###############################
def parseRecordset(recordset):
    # RegEx
    p = re.compile('[\t|]', re.IGNORECASE)


    # Read the file into a list
    jlist = []
    for line in recordset.split('\n'):
        #print line
        splitted = [ x.strip() for x in re.split(p, line) if len(x)>0]

        if(len(splitted)>1):
            jlist.append(splitted)

    '''
    # remove dups
    jlist = list(set(jlist))
    '''

    '''
    for x in jlist:
        print len(x), x
        if len(x) == 1:
            jlist.remove(x)
    '''


    #sort by Jira (col 6)
    jlist = sorted(jlist, key = itemgetter(6), reverse=True)

    #print
    for x in jlist:
        print len(x), x

    return jlist


#Need this for sorting
def itemgetter(*items):
    if len(items) == 1:
        item = items[0]
        def g(obj):
            return obj[item]
    else:
        def g(obj):
            return tuple(obj[item] for item in items)
    return g

###############
##  Save File
###############

def saveFile (jlist, label):
    folderName = "c:\\Pushout2\\"
    outputFileName = folderName + label + ".txt"
    # Write jira list in the file
    out = open(outputFileName,'w')

    #['//reReporting/Projects/Permisions.sql', '3', '2014-03-04 06:51:20', 'nbk6ntk', 'PnL-2014.03.21 ', ' GCP,GRC ', ' PNLAPP-3699 ', ' Kamal ', ' Changes for new req: UpdateReportDG\r', 'reviewd by Deepa']


    jira_prev = ''

    for item in jlist:
        #Comment line
        #CodeStory(6) Release(4) NBK(3) Time(2) DB(5) Developer(7) Comment(8)
        #comm = "REM " + item[6] + " " + item[4] + " " + item[3] + " " + item[2] + " " + item[5] + " " + item[7] + " " + item[8]

        if len(item)<9:
            print 'invalid item ', item

        comm = "REM " + item[6] + " ----------- " + item[5] + " " + item[7] + " " + item[8]

        jira = item[6]
        if jira!=jira_prev:
            print comm
            out.write("%s\n" % comm)
            jira_prev = jira

        #Script line - perforce command
        p4add = "p4 tag -a -l " + label + " " + item[10] + "#" + item[1]
        print p4add
        out.write("%s\n" % p4add)

    #out.write ('If you just reinstalled Perforce and getting errors, run "p4 set P4PORT=crpscsgap106:1667"\n')
    out.close()



if __name__ == "__main__":
   main(sys.argv[1:])

print '------ Operation completed. ------'
