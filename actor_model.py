#!/usr/bin/env python3
"""actor_model - Actor model implementation with message passing."""
import sys, threading, queue

class Actor:
    def __init__(self, name):
        self.name = name
        self.mailbox = queue.Queue()
        self._running = False
        self._thread = None
        self.processed = 0
        self.handlers = {}

    def on(self, msg_type, handler):
        self.handlers[msg_type] = handler
        return self

    def send(self, msg_type, data=None):
        self.mailbox.put((msg_type, data))

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self._running:
            try:
                msg_type, data = self.mailbox.get(timeout=0.1)
                if msg_type in self.handlers:
                    self.handlers[msg_type](data)
                self.processed += 1
            except queue.Empty:
                pass

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

class ActorSystem:
    def __init__(self):
        self.actors = {}

    def create(self, name):
        actor = Actor(name)
        self.actors[name] = actor
        return actor

    def send(self, name, msg_type, data=None):
        if name in self.actors:
            self.actors[name].send(msg_type, data)

    def start_all(self):
        for a in self.actors.values():
            a.start()

    def stop_all(self):
        for a in self.actors.values():
            a.stop()

def test():
    import time
    results = []
    sys_ = ActorSystem()
    greeter = sys_.create("greeter")
    greeter.on("greet", lambda name: results.append(f"Hello, {name}!"))
    greeter.on("farewell", lambda name: results.append(f"Bye, {name}!"))
    counter = sys_.create("counter")
    counts = [0]
    counter.on("inc", lambda _: counts.__setitem__(0, counts[0] + 1))
    counter.on("dec", lambda _: counts.__setitem__(0, counts[0] - 1))
    sys_.start_all()
    sys_.send("greeter", "greet", "World")
    sys_.send("greeter", "farewell", "World")
    sys_.send("counter", "inc", None)
    sys_.send("counter", "inc", None)
    sys_.send("counter", "dec", None)
    time.sleep(0.3)
    sys_.stop_all()
    assert "Hello, World!" in results
    assert "Bye, World!" in results
    assert counts[0] == 1
    assert greeter.processed == 2
    assert counter.processed == 3
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("actor_model: Actor system. Use --test")
