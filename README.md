This python script uses pandas to load bunch of files in SQLite via pandas and attempts to find if a common
set of data elements in all of them. The number of total files are limited to 26 at this point.
The script is coded into a executable file in a windows 10 environment using the pyinstaller utility. If anyone wants to use the tool only,they can download the exe. Python was developed against 2.7.11 environment, it should work with Python 3. Any changes to script would not change the executable automatically.

============Usage Notes===================================

This utlity allows the user to input a directory that stores a number of CSV files.
The CSV files are processed by this tool and loaded into a SQLite database.
The location of the database file happens to be the same directory where files are stored.
The tool asks users to specify a column name that is common across all CSV files.
Based on the values of this column, tool produces a HTML table that displays
one row per value that shows which files they belong to. The HTML file too is available
in the same directory wherre CSV files are present. Please ensure that
1. No more than 26 CSV files are present in the directory.
2. Each data file must have either 'csv' or 'txt' extension (lowercase)
3. Each CSV file must have a header.
4. The column user wants to compare across files, must have the same name in the header.
5. Any GUI client for SQLite 3 can be used by the user to access data stored inside database file.
6. Data in the file can be delimited by any character. User must enter it when prompted.
7. All files in the same directory must use the same delimiter.
8. If the database file is already present, system will detect it. Otherwise user must enter.
