threads
=======

   The easy Python threading module.

``threads`` is a simple module that includes

1. A decorator to easily define threaded functions.
2. Channels

A Simpler Threading Interface
-----------------------------

The ``threaded`` decorator wraps a function and causes that function to
run in a new thread when called. The function returns the
``threading.Thread`` object that the function is running in.

.. code:: python

   from threads import threaded

   @threaded
   def threaded_add(x, y):
       x + y

   threaded_add(1, 2)  # This runs in a new thread!

   def sub(x, y):
       x - y

   threaded_sub = threaded(sub)

   sub(1, 2)           # This runs in the main thread.
   threaded_sub(1, 2)  # This runs in a new thread!

This is a much simpler interface than the traditional way of starting
new threads.

Channels
--------

Channels are heavily inspired by Golang’s Channels. They are thread-safe
and allow threads to easily communicate with each other.

.. code:: python

   from threads import Channel, threaded

   from threading import current_thread

   @threaded
   def worker(num, ch):
       print 'I am worker {} in thread {}.'.format(num, current_thread().name)
       ch.send('done')  # Notify caller this thread is done.

   ch = Channel()

   for i in range(1, 5):
       worker(i, ch)  # Each call to worker runs in a new thread.

   for i in range(4):
       ch.recv()      # Wait for each worker to send the message that it's done.

   # Output:
   # I am worker 1 in thread Thread-1.
   # I am worker 2 in thread Thread-2.
   # I am worker 3 in thread Thread-3.
   # I am worker 4 in thread Thread-4.

If a channel has no value in it, calling ``recv()`` on the channel will
block that thread until a value is sent through the channel. Likewise, if there
is already a value in the channel, calling ``send()`` on the channel will
block that thread until the value is removed from the channel. In both cases,
the channel will release control to allow other threads to run.

.. warning:: The same precautions that need to be taken when using stateful
             objects across threads still applies to objects sent through
             channels. The preferred way to use channels is by passing *data*
             or *messages* through them instead of stateful objects.
