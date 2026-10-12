"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Jayden Pope>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
import queue
from common import *

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0

def worker(q):
    global call_count
    while True:
        url = q.get()
        if url is None:
             break
        item = get_data_from_server(url)
        print(f'  - {item["name"]}')
        call_count += 1




def main():
    global call_count
    q = queue.Queue()

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)


    for url in film6['characters']:
         q.put(url)
    for url in film6['planets']:
         q.put(url)
    for url in film6['starships']:
        q.put(url)
    for url in film6['vehicles']:
         q.put(url)
    for url in film6['species']:
         q.put(url)


    threads = []
    for i in range(100):
        t=threading.Thread(target=worker, args=(q,))
        threads.append(t)
        q.put(None)

    for t in threads:
         t.start()

    for t in threads:
         t.join()


    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
