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


class Channel(object):
    """A thread-safe channel to send data through."""

    def __init__(self):
        self.value = empty
        self.lock = threading.Lock()
        self.recv_val = threading.Condition(self.lock)
        self.send_val = threading.Condition(self.lock)

    def send(self, value):
        """Send a value through the channel.

        If the channel is full, sends the active thread to sleep.
        """
        with self.send_val:
            while self.value is not empty:
                # Wait for the channel to open up.
                self.send_val.wait()

            self.value = value

            self.recv_val.notify()
            # Notify the ``recv_val`` condition that the channel has a value.

    def recv(self):
        """Receive a value from the channel.

        If no value is available, sends the active thread to sleep.
        """
        with self.recv_val:
            while self.value is empty:
                # Wait for a value to be sent through the channel.
                self.recv_val.wait()

            val = self.value
            self.value = empty

            self.send_val.notify()
            # Notify the ``send_val`` condition that the channel is open.

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
