from database import Database
from node import Node
import random


class Simulation:
    def __init__(self, max_time):
        self.max_time = max_time
        self.bootstrap = Node(0, self)
        self.nodes = []
        self.event_queue = []
        self.time = 0

    def add_event(self, delta_time, function, arguments):
        event = [self.time + delta_time, function] + arguments
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda x: x[0])

    def start(self):
        database = Database("multichain.db")
        ids = database.get_identities()

        for i in range(len(ids)):
            node = Node(i+1, self)
            node.set_blocks(database.get_blocks(ids[i]))
            self.nodes.append(node)
            self.add_event(random.randint(0, 500), node.send_identity, [self.bootstrap])
        while self.event_queue:
            if self.time == self.max_time:
                event = self.event_queue.pop(0)
                self.time = event[0]
                print "Time: " + str(self.time) + " | " + str(event[1:])
                event[1](*event[2:])
            else:
                print "Time limit reached"
                return

        print "No more events"
        return



