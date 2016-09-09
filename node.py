import random


class Node:
    def __init__(self, identity, simulation):
        self.identity = identity
        self.simulation = simulation
        self.live_edges = []
        self.blocks = []

    def send_identity(self, target):
        self.simulation.add_event(self.simulation.connection_delay(), target.receive_identity, [self])

    def receive_identity(self, sender):
        self.live_edges.append(sender)

    def set_blocks(self, blocks):
        self.blocks = blocks

    def take_walk_step(self):
        if self.live_edges:
            peer = random.choice(self.live_edges)
            self.send_introduction_request(peer)
        self.simulation.add_event(5000, self.take_walk_step)

    def send_introduction_request(self, target):
        self.simulation.add_event(self.simulation.connection_delay(), target.receive_introduction_request, [self])

    def receive_introduction_request(self, sender):
        self.send_introduction_response(sender)

    def send_introduction_response(self, target):
        if self.live_edges:
            peer = random.choice(self.live_edges)
            #TODO: while peer eligble to walk
            self.simulation.add_event(self.simulation.connection_delay(), target.receive_introduction_response, [peer])
        else:
            print "I have no live edges"

    def receive_introduction_response(self, peer):
        self.live_edges.append(peer)
        self.simulation.add_event(57500, self.live_edge_timeout, [peer])

    def live_edge_timeout(self, peer):
        self.live_edges.remove(peer)
        print "I have " + str(len(self.live_edges)) + " live_edges"
