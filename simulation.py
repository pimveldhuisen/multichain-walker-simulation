from database import Database
from node import Node
import random


class Simulation:
    def __init__(self, max_time, log_file, verbose, nat_percentage):
        self.max_time = max_time
        self.bootstrap = Node(0, self)
        self.nodes = []
        self.event_queue = []
        self.time = 0
        self.log_file = log_file
        self.verbose = verbose
        assert nat_percentage < 100
        assert nat_percentage >= 0
        self.nat_percentage = nat_percentage

    def add_event(self, delta_time, function, arguments=[]):
        time = self.time + delta_time
        event = [time, function] + arguments
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda x: x[0])

    @staticmethod
    def connection_delay():
        return random.randint(100, 500)

    @staticmethod
    def initialisation_delay():
        return random.randint(0, 5000)

    def start(self):
        print "Reading multichain database.."
        database = Database("multichain.db")
        public_keys = database.get_identities()
        for public_key in public_keys:
            blocks = database.get_blocks(public_key)
            if len(blocks) > 1500:
                #TODO
                #For nodes with more than 1500 blocks, we assume these are our nodes,
                # of which we know they are not NAT'ed. This value is picked from the dataset,
                # and should probably be determined better in the future
                nat = False
            else:
                nat = random.randint(0, 100) < self.nat_percentage
            node = Node(public_key, self, nat)
            node.add_blocks(blocks)
            node.live_edges.append(self.bootstrap)
            node.send_identity(self.bootstrap)
            self.nodes.append(node)
            self.add_event(Simulation.initialisation_delay(), node.take_walk_step)

        print "Scheduling data gathering.."
        for time in range(0, self.max_time, 1000):
            self.add_event(time, self.log_data)

        print "Starting simulation.."
        while self.event_queue:
            if self.time < self.max_time:
                event = self.event_queue.pop(0)
                self.time = event[0]
                if self.verbose:
                    print "Time: " + str(self.time) + " | " + str(event[1:])
                else:
                    if self.time % 1000 == 0:
                        print self.time
                event[1](*event[2:])
            else:
                print "Time limit reached"
                return

        print "No more events"
        return

    def log_data(self):
        with open(self.log_file, 'a') as f:
            f.write(str(self.time) + " ")
        for node in self.nodes:
            if node.public_key is not 0:
                node.log_data(self.log_file)
        with open(self.log_file, 'a') as f:
            f.write("\n")

    def send_message(self, sender, target, message):
        self.add_event(Simulation.connection_delay(), target.receive_message, [sender, message])

