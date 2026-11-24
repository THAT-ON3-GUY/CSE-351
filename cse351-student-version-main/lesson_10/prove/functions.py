"""
Course: CSE 351, week 10
File: functions.py
Author: <your name>

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

I sped part 1 up at two sections, both of which are for fetching the data of individuals.
I realized that the thing repeated most often was fetching a person's data and I had to do this 
multiple times at 2 different points. First off, when getting the ids for the family and adding
them to the tree, and second when getting the info for a family's husband and wife to find their 
parents and siblings. 

So for both these sections I created a thread per request to speed up the process. This reduced
The time for 6 generations down to around 5-6 seconds.

Describe how to speed up part 2

To speed up part 2 I took the majority of what I did from part 1 and put it within a new
function that did the data requesting, getting parents/children, adding them to the tree, etc
This allowed me to thread the addition of each family to the tree. From there I then created a
queue for family id's and used a while loop that continues to run until the queue is empty.

I start by adding the first family id to the queue before starting the while loop that processes
that first family which threads the processesing of each family on that layer before starting
and joining those threads within that iteration of the loop. This kills 2 birds with one stone in
a sense as it makes sure that each layer is added to the queue before it continues making sure
the threading doesn't result in something being missed while simultaneously maintaing the idea
of a breadth first search by only allowing data from 1 layer to be processed at a time.

Extra (Optional) 10% Bonus to speed up part 3

Because different kinds of requests are being made to the server but those request are the thing
I need threaded I added a function that uses a semaphore to make those requests with. All it does
is call get_data_from_server with whatever call the request is making passed in as a parameter
using a semaphore making sure that the requests are limited to a total of 5 at any time.

"""
from common import *
import queue
import threading

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):

    def fetch_person(person_id):
        person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
        if person_data:
            tree.add_person(Person(person_data))

    if family_id is None or tree.does_family_exist(family_id):
        return

    data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    if data is None:
        return
    family = Family(data)
    tree.add_family(family)

    ids = [family.get_husband(), family.get_wife()] + family.get_children()

    person_threads = []
    for person_id in ids:
        if person_id is not None and not tree.does_person_exist(person_id):
            t = threading.Thread(target=fetch_person, args=(person_id,))
            person_threads.append(t)

    for t in person_threads:
        t.start()
    for t in person_threads:
        t.join()
                

    husband = tree.get_person(family.get_husband())
    parents = []
    if husband:
        hus_thread = threading.Thread(target=depth_fs_pedigree, args=(husband.get_parentid(), tree))
        parents.append(hus_thread)

    wife = tree.get_person(family.get_wife())
    if wife:
        wife_thread = threading.Thread(target=depth_fs_pedigree, args=(wife.get_parentid(), tree))
        parents.append(wife_thread)

    for p in parents:
        p.start()
    for p in parents:
        p.join()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree):

    q = queue.Queue()

    def fetch_person(person_id):
        person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
        if person_data:
            tree.add_person(Person(person_data))

    def process_family(fid):
        data = get_data_from_server(f'{TOP_API_URL}/family/{fid}')
        if data is None:
            return
        family = Family(data)
        tree.add_family(family)

        ids = [family.get_husband(), family.get_wife()] + family.get_children()
        threads = []
        for person_id in ids:
            if person_id is not None and not tree.does_person_exist(person_id):
                threads.append(threading.Thread(target=fetch_person, args=(person_id,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for parent_id in (family.get_husband(), family.get_wife()):
            person = tree.get_person(parent_id)
            if person and person.get_parentid() is not None:
                q.put(person.get_parentid())

    q.put(family_id)
    while not q.empty():

        level = []
        while not q.empty():
            level.append(q.get())

        threads = [threading.Thread(target=process_family, args=(fid,)) for fid in level]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):

    q = queue.Queue()
    sem = threading.Semaphore(5)

    def get_limited(url):
        with sem:
            return get_data_from_server(url)

    def fetch_person(person_id):
        person_data = get_limited(f'{TOP_API_URL}/person/{person_id}')
        if person_data:
            tree.add_person(Person(person_data))

    def process_family(fid):
        data = get_limited(f'{TOP_API_URL}/family/{fid}')
        if data is None:
            return
        family = Family(data)
        tree.add_family(family)

        ids = [family.get_husband(), family.get_wife()] + family.get_children()
        threads = []
        for person_id in ids:
            if person_id is not None and not tree.does_person_exist(person_id):
                threads.append(threading.Thread(target=fetch_person, args=(person_id,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for parent_id in (family.get_husband(), family.get_wife()):
            person = tree.get_person(parent_id)
            if person and person.get_parentid() is not None:
                q.put(person.get_parentid())

    q.put(family_id)
    while not q.empty():

        level = []
        while not q.empty():
            level.append(q.get())

        threads = [threading.Thread(target=process_family, args=(fid,)) for fid in level]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
