"""
Course    : CSE 351
Assignment: 04
Student   : Jayden Pope

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}'

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *

THREADS = 200                 # TODO - set for your program
WORKERS = 100                 # TODO - set for your program
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(input_queue, filled_input_slots, empty_input_slots, output_queue, filled_output_slots, empty_output_slots, bar):
    # TODO - fill out this thread function (and arguments)
    while True:
        filled_input_slots.acquire()
        command = input_queue.get()
        empty_input_slots.release()

        if command is None:
            break

        data = get_data_from_server(f'{TOP_API_URL}/record/{command[0]}/{command[1]}')
        empty_output_slots.acquire()
        output_queue.put((data['city'], data['date'], data['temp']))
        filled_output_slots.release()

    id = bar.wait()
    if id == 0:
        for _ in range(WORKERS):
            empty_output_slots.acquire()
            output_queue.put(None)
            filled_output_slots.release()


# ---------------------------------------------------------------------------
# TODO - Create Worker threaded class
class Worker(threading.Thread):

    def __init__(self, queue, filled_slots, empty_slots, noaa):
        threading.Thread.__init__(self)
        self.queue = queue
        self.filled_slots = filled_slots
        self.empty_slots = empty_slots
        self.noaa = noaa

    def run(self):
        while True:
            self.filled_slots.acquire()
            data = self.queue.get()
            self.empty_slots.release()

            if data is None:
                break
            self.noaa.store_data(data[0], data[1], data[2])
                

# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):
        self.noaa_lock = threading.Lock()
        self.city_dict = {}
        for city in CITIES:
            self.city_dict[city] = []

    def store_data(self, city, date, temp):
        with self.noaa_lock:
            self.city_dict[city].append((date, temp))

    def get_temp_details(self, city):

        avg_temp = 0.0

        data = self.city_dict[city]
        for instance in data:
            avg_temp += instance[1]
        return avg_temp / len(data)


# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # TODO - Create any queues, semaphores, locks or barriers you need

    retrieve_queue = Queue351()
    worker_queue = Queue351()

    retrieve_slots_filled = threading.Semaphore(0)
    retrieve_slots_empty = threading.Semaphore(10)

    worker_slots_filled = threading.Semaphore(0)
    worker_slots_empty = threading.Semaphore(10)

    retrieve_barrier = threading.Barrier(THREADS)

    retrievers = [threading.Thread(target=retrieve_weather_data, args=(retrieve_queue, retrieve_slots_filled, retrieve_slots_empty, worker_queue, worker_slots_filled, worker_slots_empty, retrieve_barrier)) for _ in range(THREADS)]

    workers = [Worker(worker_queue, worker_slots_filled, worker_slots_empty, noaa) for _ in range(WORKERS)]

    [t.start() for t in retrievers + workers]


    for name in CITIES:
        record = 0
        while record < records:
            retrieve_slots_empty.acquire()
            retrieve_queue.put((name, record))
            retrieve_slots_filled.release()
            record += 1
    for _ in range(THREADS):
        retrieve_slots_empty.acquire()
        retrieve_queue.put(None)
        retrieve_slots_filled.release()
    print("Done adding commands to queue.")
    

    [t.join() for t in retrievers + workers]


    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

