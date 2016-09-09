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

    def add_event(self, delta_time, function, arguments=[]):
        event = [self.time + delta_time, function] + arguments
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda x: x[0])

    @staticmethod
    def connection_delay():
        return random.randint(100, 500)

    def start(self):
        print "Reading multichain database.."
        database = Database("multichain.db")
        ids = database.get_identities()
        for i in range(len(ids)):
            node = Node(i+1, self)
            node.set_blocks(database.get_blocks(ids[i]))
            node.live_edges.append(self.bootstrap)
            node.send_identity(self.bootstrap)
            self.nodes.append(node)
            self.add_event(Simulation.connection_delay(), node.take_walk_step)

        print "Starting simulation.."
        while self.event_queue:
            if self.time < self.max_time:
                event = self.event_queue.pop(0)
                self.time = event[0]
                print "Time: " + str(self.time) + " | " + str(event[1:])
                event[1](*event[2:])
            else:
                print "Time limit reached"
                return

        print "No more events"
        return
