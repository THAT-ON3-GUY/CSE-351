""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: <Student Name>

See instructions in canvas for this team activity.

"""

import random
import threading

# Include CSE 351 common Python files. 
from cse351 import *

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

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
def producer(que, bar, filled, empty):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        empty.acquire()
        que.put(number)
        filled.release()

    id = bar.wait()
    if id == 0:
        for _ in range(CONSUMERS):
            empty.acquire()
            que.put(None)
            filled.release()
   

# ---------------------------------------------------------------------------
def consumer(que, filled, empty, lock_file):
    while True:
        filled.acquire()
        num = que.get()
        empty.release()

        if num is None:
            break
        if is_prime(num):
            with lock_file:
                with open(FILENAME, "a") as f:
                    f.write(f'{num}\n')
# ---------------------------------------------------------------------------
def main():

    random.seed(102030)

    que = Queue351()

    filled = threading.Semaphore(0)
    empty = threading.Semaphore(10)

    barrier = threading.Barrier(3)
    lock_file = threading.Lock()

    # TODO - create producers threads (see PRODUCERS value)
    pros = [threading.Thread(target=producer, args=(que, barrier, filled, empty)) for _ in range(PRODUCERS)]
    # TODO - create consumers threads (see CONSUMERS value)
    cons = [threading.Thread(target=consumer, args=(que, filled, empty, lock_file)) for _ in range(CONSUMERS)]

    [t.start() for t in pros + cons]
    [t.join() for t in pros + cons]

    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            primes = len(f.readlines())
    else:
        primes = 0
    print(f"Found {primes} primes. Must be 108 found.")



if __name__ == '__main__':
    main()
