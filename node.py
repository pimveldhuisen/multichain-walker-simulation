import random


class Node:
    def __init__(self, id, simulation):
        self.id = id
        self.simulation = simulation
        self.live_edges = []
        self.blocks = []

    def send_identity(self, target):
        self.simulation.add_event(random.randint(0, 500), target.receive_identity, [self.id])

    def receive_identity(self, sender):
        self.live_edges.append(sender)

    def set_blocks(self, blocks):
        self.blocks = blocks
        print "I have " + str(len(blocks)) + " blocks"
