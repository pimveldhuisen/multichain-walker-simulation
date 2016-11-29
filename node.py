import random
import os
import base64

from database import Database


class Node:

    NAT_TIMEOUT = 60000     # Time before the NAT will close a hole
    NAT_TIMEOUT_WITH_MARGIN = 57500     # Maximum Time after puncturing a NAT at which we assume
    # a message can still reach the target before the hole closes (ms)
    WALK_STEP_TIME = 5000   # Interval at which we do walk steps (ms)

    def __init__(self, public_key, simulation, nat=False):
        self.public_key = public_key
        self.simulation = simulation
        self.live_edges = []
        self.node_directory = "nodes/" + base64.encodestring(str(self.public_key))
        if not os.path.exists(self.node_directory):
            os.makedirs(self.node_directory)
        self.block_database = Database(self.node_directory + "/multichain.db")
        self.log = open(self.node_directory + "/log.txt", 'w')
        self.nat = nat

    def receive_message(self, sender, message):
        message['function'](*message['arguments'])

    def send_message(self, target, message):
        self.simulation.send_message(self, target, message)

    def send_identity(self, target):
        message = dict()
        message['function'] = target.receive_identity
        message['arguments'] = [self]
        self.send_message(target, message)

    def receive_identity(self, sender):
        self.live_edges.append(sender)

    def add_blocks(self, blocks):
        self.block_database.add_blocks(blocks)
        self.log.write("Added " + str(len(blocks)) + " blocks to my database, I now have " +
                       str(self.block_database.get_number_of_blocks_in_db()) + " blocks\n")

    def take_walk_step(self):
        if self.live_edges:
            peer = random.choice(self.live_edges)
            self.send_introduction_request(peer)
        self.simulation.add_event(5000, self.take_walk_step)

    def send_introduction_request(self, target):
        message = dict()
        message['function'] = target.receive_introduction_request
        message['arguments'] = [self]
        self.send_message(target, message)

    def receive_introduction_request(self, sender):
        self.send_introduction_response(sender)

    def send_introduction_response(self, target):
        if self.live_edges:
            peer = random.choice(self.live_edges)
            #TODO: while peer eligble to walk
            message = dict()
            message['function'] = target.receive_introduction_response
            message['arguments'] = [peer]
            self.send_message(target, message)
        else:
            print "I have no live edges"

    def receive_introduction_response(self, peer):
        self.live_edges.append(peer)
        self.simulation.add_event(57500, self.live_edge_timeout, [peer])
        self.send_crawl_request(peer)

    def live_edge_timeout(self, peer):
        self.live_edges.remove(peer)

    def send_crawl_request(self, target):
        message = dict()
        message['function'] = target.receive_crawl_request
        message['arguments'] = [self]
        self.send_message(target, message)

    def receive_crawl_request(self, sender):
        if self.public_key is not 0:
            self.send_crawl_response(sender)

    def send_crawl_response(self, target):
        blocks = self.block_database.get_blocks(self.public_key)
        message = dict()
        message['function'] = target.receive_crawl_response
        message['arguments'] = [blocks]
        self.send_message(target, message)

    def receive_crawl_response(self, blocks):
        self.add_blocks(blocks)

    def log_data(self, datafile):
        with open(datafile, 'a') as f:
            f.write(str(self.block_database.get_number_of_blocks_in_db()) + " ")




