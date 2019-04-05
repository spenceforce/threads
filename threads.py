"""Threads

The easy Python threading module.
"""
from functools import wraps
try:
    import threading
except ImportError:
    import dummy_threading as threading


class Empty(object):
    """An empty value.
    
    ``Empty`` is a uniquely identifiable object that signifies a ``Channel`` is
    empty. ``False`` or ``None`` are inappropriate for this purpose since those
    values could be sent through the ``Channel``.
    """

    def __repr__(self):
        return "<Empty>"


empty = Empty()                 # The empty value.


class _Queue(object):
    """Simple wrap-around queue.

    :param int size: The size of the queue.
    """

    def __init__(self, size=1):
        self._queue = [empty for _ in range(size)]
        self._start = self._end = 0

    def __getitem__(self, key):
        return self._queue[key]

    def __setitem__(self, key, value):
        self._queue[key] = value

    def __len__(self):
        return len(self._queue)

    @property
    def empty(self):
        """Return bool indicating if queue is empty."""
        return self._queue[self._start] is empty

    @property
    def full(self):
        """Return bool indicating if queue is full."""
        return self[self._end] is not empty

    def _inc_index(self, index):
        """Properly increment the index and return."""
        return (index + 1) % len(self)

    def pop(self):
        """Pop a value from the front of the queue.

        :raises ValueError: When the queue is empty.
        """
        if self.empty:
            # This should never happen if the queue is managed properly.
            raise ValueError('Cannot pop from empty queue.')

        val = self[self._start]

        self[self._start] = empty
        self._start = self._inc_index(self._start)

        return val

    def push(self, value):
        """Push the value onto the back of the queue.

        :raises ValueError: When the queue is full.
        """
        if self.full:
            # This should never happen if the queue is managed properly.
            raise ValueError('Cannot push onto full queue.')

        self[self._end] = value
        self._end = self._inc_index(self._end)


class Channel(object):
    """A thread-safe channel to send data through.

    :param int size: The size of the channels buffer.
    """

    def __init__(self, size=1):
        self._values = _Queue(size)
        self._lock = threading.Lock()
        self._recv_val = threading.Condition(self._lock)
        self._send_val = threading.Condition(self._lock)

    def send(self, value):
        """Send a value through the channel.

        If the channel is full, sends the active thread to sleep.
        """
        with self._send_val:
            while self._values.full:
                # Wait for the channel to open up.
                self._send_val.wait()

            self._values.push(value)

            # Notify the ``recv_val`` condition that the channel has a value.
            self._recv_val.notify()

    def recv(self):
        """Receive a value from the channel.

        If no value is available, sends the active thread to sleep.
        """
        with self._recv_val:
            while self._values.empty:
                # Wait for a value to be sent through the channel.
                self._recv_val.wait()

            val = self._values.pop()

            # Notify the ``send_val`` condition that the channel is open.
            self._send_val.notify()

            return val


def threaded(f):
    """Create a threaded function.

    :param f: A function.
    :returns: A ``threading.Thread`` object that the function is running in.

    :example:
        @threaded
        def threaded_add(x, y):
            x + y

        threaded_add(1, 2)  # This runs in a new thread!

    :example:
        def add(x, y):
            x + y

        threaded_add = threaded(add)

        add(1, 2)           # This runs in the main thread.
        threaded_add(1, 2)  # This runs in a new thread!
    """
    @wraps(f)
    def threaded_wrapper(*args, **kwargs):
        t = threading.Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        return t
    return threaded_wrapper
