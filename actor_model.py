#!/usr/bin/env python3
"""Actor model — message passing concurrency simulation."""
import sys
from collections import deque

class Actor:
    def __init__(self, name):
        self.name = name
        self.mailbox = deque()
        self.state = {}
        self.handlers = {}
    def on(self, msg_type, handler):
        self.handlers[msg_type] = handler
    def send(self, msg_type, data=None):
        self.mailbox.append((msg_type, data))
    def process_one(self):
        if not self.mailbox: return False
        msg_type, data = self.mailbox.popleft()
        if msg_type in self.handlers:
            self.handlers[msg_type](self, data)
        return True
    def process_all(self):
        count = 0
        while self.process_one():
            count += 1
        return count

class ActorSystem:
    def __init__(self):
        self.actors = {}
    def create(self, name):
        a = Actor(name)
        self.actors[name] = a
        return a
    def send(self, target, msg_type, data=None):
        if target in self.actors:
            self.actors[target].send(msg_type, data)
    def run(self, max_steps=1000):
        total = 0
        for _ in range(max_steps):
            processed = sum(a.process_one() for a in self.actors.values())
            total += processed
            if processed == 0: break
        return total

def test():
    sys_ = ActorSystem()
    counter = sys_.create("counter")
    counter.state["count"] = 0
    counter.on("inc", lambda self, data: self.state.__setitem__("count", self.state["count"] + (data or 1)))
    counter.on("get", lambda self, data: None)
    sys_.send("counter", "inc", 5)
    sys_.send("counter", "inc", 3)
    sys_.send("counter", "inc")
    processed = sys_.run()
    assert processed == 3
    assert counter.state["count"] == 9
    # Actor-to-actor
    logger = sys_.create("logger")
    logger.state["log"] = []
    logger.on("log", lambda self, data: self.state["log"].append(data))
    counter.on("notify", lambda self, data: sys_.send("logger", "log", f"count={self.state['count']}"))
    sys_.send("counter", "notify")
    sys_.run()
    assert logger.state["log"] == ["count=9"]
    print("  actor_model: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Actor model simulation")
