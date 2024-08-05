import random
from queue import Queue
import sys
import logging


def make_dict_hashable(d):
    """
    Convert a dictionary to a hashable frozenset of tuples.

    :param d: Dictionary to convert.
    :return: Hashable frozenset of dictionary items.
    """
    if not isinstance(d, dict):
        raise TypeError('Expected a dictionary')
    # Recursively convert dictionary items to tuples and make them hashable
    return frozenset((key, make_value_hashable(value)) for key, value in sorted(d.items(), key=lambda item: item[0]))


def make_value_hashable(value):
    """
    Recursively convert a value to a hashable type.

    :param value: Value to convert.
    :return: Hashable representation of the value.
    """
    if isinstance(value, dict):
        return make_dict_hashable(value)
    elif isinstance(value, list):
        return tuple(make_value_hashable(v) for v in sorted(value, key=lambda item: item))
    elif isinstance(value, set):
        return frozenset(make_value_hashable(v) for v in sorted(value, key=lambda item: item))
    return value


# Function to randomly sort items in a queue
def random_sort_queue(queue):
    """
    Randomly sort items in a queue.

    :param queue: Queue to sort.
    :return: Queue with items in random order.
    """
    items = []

    # Dequeue all items and store them in a list
    while not queue.empty():
        items.append(queue.get())

    # Shuffle the list of items
    random.shuffle(items)

    # Enqueue the items back into the queue in random order
    for item in items:
        queue.put(item)

    return queue


# Function to create a queue from a list
def create_queue_from_list(items):
    """
    Create a queue from a list of items.

    :param items: List of items to add to the queue.
    :return: Queue containing the items.
    """
    queue = Queue()
    for item in items:
        queue.put(item)  # Enqueue each item
    return queue


def set_log(level):
    """
    Set up logging configuration.

    :param level: Logging level to set.
    """
    logger = logging.getLogger('DBG')
    # Stream/console output
    logger.handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(level)
    logger.handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger.handler.setFormatter(formatter)
    logger.addHandler(logger.handler)


def log(msg):
    """
    Log a message at the INFO level.

    :param msg: Message to log.
    """
    logger = logging.getLogger('DBG')
    logger.info(msg)


def split_list_into_chunks(lst, chunk_size):
    """
    Split a list into chunks of a specified size.

    :param lst: List to split.
    :param chunk_size: Size of each chunk.
    :return: List of chunks.
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
