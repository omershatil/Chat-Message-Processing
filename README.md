# The problem:

Write a program that reads and processes a '\n' delimited input file, where each line is a JSON encoded message in one of the following formats.

### Chat Message

    {
      "id":"45094d07-e2cf-11e4-9454-56847afe9799",
      "from":"visitor5",
      "type":"message",
      "site_id":"123",
      "data":{
        "message":"Hi, how's it going",
      },
      "timestamp":1429026445,
    }

This message represents text sent from a website visitor to a site ("site_id").

### Status

    {
      "id":"53367bc7-e2cf-11e4-81da-56847afe9799",
      "from":"operator1",
      "site_id":"123",
      "type":"status",
      "data":{
        "status":"online",
      }
      "timestamp":1429026448,
    }

This message represents a chat operator signing either "online" or "offline".

## Processing

While reading through the file, the program should create and maintain a summary of activity, either in memory or in an external datastore of your choosing.

Messages *are not* guaranteed to be in order while processing. Every unique message will have a unique "id", but it may be sent more than once. You should make an effort to not process duplicate messages. Every unique message will also have a unique timestamp.

Each site (indicated by "site_id" in all messages) represents an account in our system. If a site has at least one operator signed online, we consider that site "online" and website visitors will be able to send chat messages to the operators for that site. If there are no operators online, the site will be considered "offline" and a visitor's messages will be sent via email instead of chat. You should track which messages are sent via chat, and which are sent via email. You can assume that all sites start in an "offline" mode.

After processing, your program should output to stdout a summary of chat activity, one line per site containing the number of chat messages sent, the number of emails sent, as well as a count of the number of unique visitor IDs + unique operator IDs seen throughout processing.

    site_id,messages=count,emails=count,operators=count,visitors=count

Output should be ordered by alphanumerically ascending site ID, for example:

    123,messages=1,emails=0,operators=1,visitors=2
    124,messages=2,emails=1,operators=4,visitors=1
    ...

## Validation

Sample input and output files are included.

We will test your program with at least 10M lines of input, and run it on a machine with approximately 2GB of RAM.

## Musts

 1. Can be written in language of your choosing
 1. Include a README describing how to build and run your program
 1. Can use memory only, or any external database or similar of your choosing
 1. Build and run on an Ubuntu 12.04 machine without much fuss
   * open to interpretation, but safe to say you shouldn't rely on that one bug in IRIX 5.3's XFS implementation, etc.
   * any external database you use should be simply installable by `apt-get` or language tooling (`pip`, `go get`, `gem`, etc.)
 1. Present correct output
 1. Survive failure: if your program and/or database is force killed, the eventual output should still be correct 
 1. While speed is important, come prepared to talk about how you've chosen to architect your solution, and how you would add new features or support different constraints



## Nice-to-haves

 1. Avoid reprocessing from the start in the case of a restart after a failure
 1. Avoid reprocessing duplicate messages

THE SOLUTION:
=============
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

