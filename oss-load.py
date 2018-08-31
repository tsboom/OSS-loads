#!/usr/bin/env python
import os.path
import time
import subprocess
from subprocess import call, Popen, PIPE
import csv
import sys
import pdb
import re
import pprint
# debugging: insert  pdb.set_trace() to set breakpoint

# get filename argument from the shell (ex: python oss-load.py filename.csv)
csv_file = sys.argv[1]

# open csv file for checking
f = open(csv_file)
reader = csv.reader(f)
# skip headers
next(reader, None)

# functions that do basic checks to figure out which fields are provided
def is_barcode(value):
    regex = r"[0-9]{14}"
    if re.search(regex, value):
        return True

def is_rmst(value):
    regex = r"R[0-9]{2}M[0-9]{2}S[0-9]{2}T[0-9]{2}"
    #regex = r"Z[0-9]{2}M[0-9]{2}S[0-9]{2}T[0-9]{2}"
    if re.search(regex, value):
        return True
        
# variable to describe the type of CSV after it is checked
csv_type = ""

# variable to hold the ordered dictionary version of the CSV
csv_dict = []
for row in reader: 
    csv_dict.append(row)

# iterate over rows in the new csv dict
pp = pprint.PrettyPrinter(indent=4)
for row in csv_dict:
    print ".........."
    pp.pprint(row) 
    print "\n\nrow length is: " + str(len(row)) +"\n\n"
    if len(row) > 5:
        print "Error: There are too many columns. Please check the data and try again."
    elif len(row) == 5 and is_rmst(row[0]):
        # check to make sure size is valid
        valid_sizes = ['A', 'B', 'C', 'D', 'E', 'M', 'O', 'P', 'U']
        if any(size in row[2] for size in valid_sizes):
            csv_type = "RMST, full, size, height, source"
        else:
            print "Error: Please check your size and height values. The third column should be a letter code for size."
    elif len(row) == 4 and is_barcode(row[0]):
        csv_type = "barcode, title, author, call number"
    elif len(row == 3 and is_barcode(row[0]) and is_rmst(row[1])):
        csv_type = "barcode, RMST, title"
    else: 
        print "Error: There is a problem with the CSV file. Please check the data and try again."
    f.close()
    break
    
print "CSV type: " + csv_type + "\n\n" 

# set up SQL file
# name the SQL file the same name as the CSV, but with a .sql extension
filename_no_ext = os.path.splitext(csv_file)[0]
sql_file = filename_no_ext + '.sql'
f = open(sql_file, "w")
print "sql_file: " + sql_file + "\n\n"

# function to run build_sql script on the csv_file using subprocess
def build_sql(scriptname, csv_file):
    subprocess.call(["./"+scriptname, csv_file], stdout=f)

# build SQL using the build_sql script which corresponds to csv_type
if csv_type == "barcode, RMST, title":
    build_sql('build_sql_0307a', csv_file)
if csv_type == "RMST, full, size, height, source":
    build_sql('build_sql_0307b', csv_file)
if csv_type == "barcode, title, author, call number":
    build_sql('build_sql_0314', csv_file)
    
# check if SQL file exists 
while not os.path.exists(sql_file):
    print "Waiting for SQL file..."
    time.sleep(1)

# function to run sql queries in file
def run_sql_queries():
    # s+ is an alias for sqlplus !:1/`get_ora_passwd !:1`
    session = Popen(['get_ora_passwd','moss'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = session.communicate()
    password = output
    login_string = "moss/"+password
    #pdb.set_trace()
    session = Popen(['sqlplus', '-s', login_string], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    session.stdin.write('set feedback off\n')
    print "Executing SQL file..."
    session.stdin.write('@'+ filename_no_ext +';')
    ## communicate results to stdout
    #return session.communicate(i)
    return session



# make sure SQL file exists, then run the process
try:
    if os.path.isfile(sql_file) == False:
       raise Exception
except ValueError as e:
    print('There is an error with the sql file')
else:
    print "Opening SQL Plus"
    # opens Sql plus session and saves results
    query_result, error_messages = run_sql_queries().communicate() 
    print "---\n\nSQL Plus results:\n\n" + str (query_result) + "\n\n"
    print "---\n\nError messages:\n\n" + str(error_messages) + "\n\n"
    # commit changes
    session.stdin.write('commit;')
finally:
   print "\n\nExiting the database\n\n"
   session.stdin.write('quit;')

