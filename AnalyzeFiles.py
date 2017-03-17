#!/usr/bin/python
# PURPOSE: This script uses pandas to load bunch of files in SQLite via pandas and attempts to find if a common
#          set of data elements in all of them. The number of total files are limited to 26 at this point.
# CHANGE CONTROL:
# Sid Chatterjee     Draft

from __future__ import with_statement, nested_scopes, generators, division, absolute_import, print_function, \
    unicode_literals
import sqlite3
from six.moves import input   #For python 3
import os, os.path
import pandas as pd
import glob
from functools import reduce   # For python 3


if __name__ == '__main__':
    print('='* 75)
    print("This utlity allows the user to input a directory that stores a number of CSV files.")
    print("The CSV files are processed by this tool and loaded into a SQLite database.")
    print("The location of the database file happens to be the same directory where files are stored.")
    print("The tool asks users to specify a column name that is common across all CSV files.")
    print("Based on the values of this column, tool produces a HTML table that displays ")
    print("one row per value that shows which files they belong to. The HTML file too is available")
    print("in the same directory wherre CSV files are present. Please ensure that")
    print("1. No more than 26 CSV files are present in the directory.")
    print("2. Each data file must have either 'csv' or 'txt' extension (lowercase)")
    print("3. Each CSV file must have a header.")
    print("4. The column user wants to compare across files, must have the same name in the header.")
    print("5. Any GUI client for SQLite 3 can be used by the user to access data stored inside database file.")
    print("6. Data in the file can be delimited by any character. User must enter it when prompted.")
    print("7. All files in the same directory must use the same delimiter.")
    print("8. If the database file is already present, system will detect it. Otherwise user must enter.")
    print("="*75)
    dataDirectory = input('Enter directory where files are stored (press enter to cancel):')
    if dataDirectory == '':
        print("Execution cancelled.")
        exit(1)
    dbFileFound=0
    for dbFile in glob.glob(dataDirectory+os.sep+'*.sqlite3'):
        dbFileName=dbFile
        dbFileFound=1
    if dbFileFound == 0:
        dbFileName = input('Enter the name of database file:')
        if not dbFileName.endswith('.sqlite3'):
            dbFileName = dbFileName + '.sqlite3'
    else:
        print("Found the databasefile {}".format(dbFileName))
    dataBase = sqlite3.connect(dataDirectory + os.sep + dbFileName.split(os.sep)[-1])
    dataBase.text_factory = str
    sep=input('Enter the separator for the files:')
    dataFiles=[]
    aliasList=[]
    aliasBase=0
    for root, dirNames, fileNames in os.walk(dataDirectory):
        for fileName in fileNames:
            if not fileName.endswith('.csv') and not fileName.endswith('.txt'):
                continue
            dataFiles.append(fileName)
            if len(dataFiles) > 26:
                print("More than 26 files in the directory. Exitting.")
                exit(1)
            pd_frames = pd.read_csv(dataDirectory + os.sep + fileName, sep=str(sep), delimiter=str(sep),
                                              header=0, engine='c', skipinitialspace=True)
            pd_frames.to_sql(fileName, dataBase, if_exists='replace')
    commonColumnName = input("Enter the column name to compare with:")
    joinStaticClause = ' USING ' + '("' + commonColumnName + '")'
    firstTable = '"{}"'.format(dataFiles[0])
    joinClause = map(lambda anchorTable: '{} {}'.format(anchorTable, ' '.join(map(lambda tableName: \
                    'LEFT JOIN {} {}'.format(tableName, joinStaticClause),['"{}"'.format(tableName)
                    for tableName in dataFiles if anchorTable.find(tableName) == -1]))),['"{}"'.format(tableName)
                    for tableName in dataFiles])
    selectClause=map(lambda atable: """SELECT "{f1}"."{f2}" "Data Element", {f3} FROM """.format(f1=atable, f2=commonColumnName,
                     f3=', '.join(map(lambda tname: \
                    """CASE WHEN "{f1}"."{f2}" IS NULL THEN 'NOT EXISTS' ELSE 'EXISTS' END "Exists in {f1}?" """
                    .format(f1=tname, f2=commonColumnName), [tname for tname in dataFiles]))),
                     dataFiles)
    sql=reduce(lambda clause1, clause2: '{} UNION {}'.format(clause1, clause2), ['{} {}'.format(*tableName) \
                for tableName in zip(selectClause, joinClause)])
    outputData=pd.read_sql("""SELECT "Data Element", {} FROM ({}) TAB GROUP BY "Data Element" """.format(', '.\
                        join(map(lambda string1: 'MIN("Exists in {f1}?") "Exists in {f1}?"'.\
                        format(f1=string1), dataFiles)),sql), dataBase)
    with open(dataDirectory+os.sep+'.'.join(dbFileName.split(os.sep)[-1].split('.')[:-1])+'.htm','w') as writeOutput:
        writeOutput.write(outputData.to_html().replace(
            '<td>EXISTS</td>','<td><p style="background-color: #00FF7F">EXISTS</p></td>').replace(
            '<td>NOT EXISTS</td>','<td><p style="background-color: #EB7C92">NOT EXISTS</td>'
        ))
