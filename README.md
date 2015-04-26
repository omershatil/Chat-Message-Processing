Installation and Execution:
--------------------------
- There are no installation steps. The script works with the standard Python 2.7 modules.
- Execution:
From the chat_message_processing folder execute the script. 
Example:
python omer/messageprocessing/process_chat_messages.py -f datafiles\small_input -p 100000  -t True

usage: process_message_readline.py [-h] -f FILE_PATH [-p PAGE_LINE_SIZE]
                                   [-m MARSHAL_FOLDER] [-t PRINT_TIMING_DATA]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_PATH, --file-path FILE_PATH
  -p PAGE_LINE_SIZE, --page_line_size PAGE_LINE_SIZE
  -m MARSHAL_FOLDER, --marshal_folder MARSHAL_FOLDER
  -t PRINT_TIMING_DATA, --print_timing_data PRINT_TIMING_DATA

NOTES:
-----
1) The bigger the value passed as PAGE_LINE_SIZE (or -p) the faster the script will complete execution. The number
passed indicates the number of lines after which a persistence occurs. So, if you pass "-p 100000" the script will
save state every 100000 lines are processed. If the script crashes, it will be able to restart after the last 100000
persisted lines.

2) The PRINT_TIMING_DATA option (-t) prints some detail about how long it took to: read the file in, parse it and save
needed portion of it in memory, save the state (and how many time the state was saved), and how long it took to calculate and generate the final report.

3) The MARSHAL_FOLDER option (-m) indicates where the script should save the persisted state on disk.

DISCUSSION:
==========
1) Python does a great job of buffering while reading the text file. Initially I thought I'd need to attempt to improve upon the speed of streaming the file in, but as I ran the timing code I saw that reading was not the bottle-neck for performance. Python reads ahead as the code processes each line so there doesn't seem any delay waiting for data.

2) regex parsing is, as expected, significantly faster than json/ast of dictionary building. Huge performance gains using it. Initially I tried json and ast but both were too slow (ast worse).

3) I chose to use Python even though I have more experience with Java and could utilize threading in Java to take
advantage of multi-process systems to process the data once loaded to memory.

4) I chose to save the state into a file because it's simple. I will later try to use a database and compare performance.


POSSIBLE IMPROVEMENTS:
---------------------
1) Unit tests.

2) Use a database (NoSQL and/or SQL) and compare performance with persistence into a file. That will also solve the lack of atomic operation

for renaming the temporary file (problem on Windows only). The most important gain could be from saving the state. Other techniques could be tried for improved calculation with a database (maybe even a stored procedure?).

3) Log. 

4) Handle corrupt data (partial json). Log duplicates.

4) Read file from remote location (HTTP/FTP site or SSH/SCP)

5) Reduce hard-coding of values in code (like json entries). Could read json schema and use that.

6) Could re-write using a big-data solution like Hadoop, but that would require a cluster...

