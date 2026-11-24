""" 
Course: CSE 351
Team  : 
File  : Week 9 team.py
Author:  Luc Comeau
"""

# Include CSE 351 common Python files. 
from cse351 import *
import time
import random
import multiprocessing as mp
from multiprocessing import Pool

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))

def cleaner(cleaner_id, times_cleaned, cleaning_lock, start_time, end_time):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    while start_time <= end_time:
        cleaner_waiting()

        with cleaning_lock:
            print(STARTING_CLEANING_MESSAGE)
            times_cleaned += 1
            cleaner_cleaning(cleaner_id)
            print(STOPPING_CLEANING_MESSAGE)


def guest(guest_id, headcount, party_num, light_lock, cleaning_lock, start_time, end_time):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while start_time <= end_time:
        guest_waiting()
        with light_lock:
            headcount += 1
            if headcount == 1:
                print(STARTING_PARTY_MESSAGE)
                cleaning_lock.acquire()
            
        guest_partying(guest_id, headcount)

        with light_lock:
            headcount -= 1
            party_num += 1
            if headcount == 0:
                print(STOPPING_PARTY_MESSAGE)
                cleaning_lock.release()


def main():
    # Start time of the running of the program.
    start_time = time.time()
    end_time = start_time + 60

    # TODO - add any variables, data structures, processes you need
    # TODO - add any arguments to cleaner() and guest() that you need

    with mp.Manager() as man:
        light_lock = man.Lock()
        cleaning_lock = man.Lock()
        guest_count = man.Value('i', 0)
        party_count = man.Value('i', 0)
        cleaned_count = man.Value('i', 0)

    for i in range(HOTEL_GUESTS):
        hg = mp.Process(target=guest, args=(i+1, guest_count, party_count, light_lock, cleaning_lock, start_time, end_time))
        hg.start()

    for i in range(CLEANING_STAFF):
        cs = mp.Process(target=cleaner, args=(i+1, cleaned_count, cleaning_lock, start_time, end_time))
        cs.start()

    # Results
    print(f'Room was cleaned {cleaned_count} times, there were {party_count} parties')


if __name__ == '__main__':
    main()
