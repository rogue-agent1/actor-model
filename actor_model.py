#!/usr/bin/env python3
"""actor_model - Actor system with message passing and supervision."""
import sys, threading, queue

class Actor:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler
        self.mailbox = queue.Queue()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    def _loop(self):
        while self._running:
            try:
                msg = self.mailbox.get(timeout=0.1)
                self.handler(self, msg)
            except queue.Empty:
                continue
    def send(self, msg):
        self.mailbox.put(msg)
    def stop(self):
        self._running = False
        self._thread.join(timeout=2)

class ActorSystem:
    def __init__(self):
        self.actors = {}
    def spawn(self, name, handler):
        a = Actor(name, handler)
        self.actors[name] = a
        return a
    def send(self, name, msg):
        if name in self.actors:
            self.actors[name].send(msg)
    def stop_all(self):
        for a in self.actors.values(): a.stop()

def test():
    results = []
    lock = threading.Lock()
    def echo_handler(actor, msg):
        with lock: results.append((actor.name, msg))
    sys_ = ActorSystem()
    a1 = sys_.spawn("echo1", echo_handler)
    a2 = sys_.spawn("echo2", echo_handler)
    a1.send("hello")
    a2.send("world")
    a1.send("foo")
    import time; time.sleep(0.3)
    sys_.stop_all()
    assert len(results) == 3
    echo1_msgs = [r[1] for r in results if r[0] == "echo1"]
    assert echo1_msgs == ["hello", "foo"]
    echo2_msgs = [r[1] for r in results if r[0] == "echo2"]
    assert echo2_msgs == ["world"]
    print("actor_model: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: actor_model.py --test")
