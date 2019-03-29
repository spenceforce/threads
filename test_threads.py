"""Tests"""
import time
try:
    import threading
except ImportError:
    import dummy_threading as threading

import pytest

from threads import Channel, empty, threaded


# Helper functions
# ----------------
def yield_control():
    """Yield control to another thread."""
    time.sleep(0.1)

# Fixtures
# --------
@pytest.fixture()
def loaded_ch():
    """Provides a value and a channel loaded with that value."""
    val = object()
    ch = Channel()
    ch.send(val)
    return val, ch

def test_send():
    val = object()
    ch = Channel()
    ch.send(val)
    assert ch.value is val

def test_recv(loaded_ch):
    val, ch = loaded_ch
    assert ch.recv() is val
    assert ch.value is empty

def test_recv_waits_in_different_thread():
    val = object()
    ch = Channel()

    def f(ch):
        assert ch.recv() is val  # This will block until a value is sent.

    t = threading.Thread(target=f, args=(ch,))
    t.start()

    # Release control to other thread ``t``.
    yield_control()

    ch.send(val)

    t.join()                    # Ensure thread finishes.

def test_send_waits_in_different_thread():
    val = object()
    ch = Channel()
    ch.send(object())
    # Preload channel to force ``send`` to wait in other thread.

    def f(ch):
        ch.send(val)            # This will block until a value is received.
        assert ch.value is val

    t = threading.Thread(target=f, args=(ch,))
    t.start()

    # Release control to other thread ``t``.
    yield_control()

    assert ch.recv() is not val
    # Ensure item received is not the second value sent through channel.

    t.join()                    # Ensure thread finishes.

def test_threaded_wrapper():
    main_thread = threading.current_thread()
    val = object()

    @threaded
    def f(v):
        assert threading.current_thread() is not main_thread
        assert v is val

    f(val).join()
