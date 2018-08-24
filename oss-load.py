#!/usr/bin/env python
import os.path
import time
from subprocess import Popen, PIPE
import csv
import pdb
import re
# debugging: insert  pdb.set_trace() to set breakpoint

# get filename argument from the shell (ex: python oss-load.py filename.csv)
csv_file = sys.argv[1]

# open csv file for checking
f = open(csv_file)
reader = csv.DictReader(f)

#skip first line
reader.readline()

# functions that do basic checks to figure out which fields are provided
def is_barcode(value):
    regex = r"[0-9]{14}"
    if re.search(regex, value):
        return true

def is_rmst(value):
    regex = r"R[0-9]{2}M[0-9]{2}S[0-9]{2}T[0-9]{2}"
    if re.search(regex, value):
        return true
        
# variable to describe the type of CSV after it is checked
csv_type = ""
for row in reader: 
    if len(row) > 5:
        print "Error: There are too many columns. Please check the data and try again."
        f.close()
        break
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

# set up SQL file
# name the SQL file the same name as the CSV, but with a .sql extension
filename_no_ext = os.path.splittext(csv_file)[0]
sql_file = filename_no_ext + '.sql'
f = open(sql_file, "w")

# function to run build_sql script on the csv_file using subprocess
def build_sql(scriptname, csv_file):
    subprocess.call(["./"+scriptname, csv_file], stdout=f)

# build SQL using the build_sql script which corresponds to csv_type
if csv_type = "barcode, RMST, title":
    build_sql('build_sql_0307a', csv_file)
if csv_type = "RMST, full, size, height, source":
    build_sql('build_sql_0307b', csv_file)
if csv_type = "barcode, title, author, call number":
    build_sql('build_sql_0314', csv_file)
    
# check if SQL file exists 
while not os.path.exists(sql_file):
    time.sleep(1)

if os.path.isfile(sql_file):
    # opens Sql plus session
    session = Popen([‘s+’,’moss’], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    session.stdin.write('set feedback off;')
    session.stdin.write('@'+ filename_no_ext +';')
    # communicate results to stdout
    stdout, stderr = session.communicate()
    
else:
    raise ValueError("%s isn't a file!" % file_path)
