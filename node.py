import random
import os
import base64

from database import Database
from scoring import get_ranking, calculate_ranking_similarity


class Node:
    NAT_TIMEOUT = 60000     # Time before the NAT will close a hole
    NAT_TIMEOUT_WITH_MARGIN = 57500     # Maximum Time after puncturing a NAT at which we assume
    # a message can still reach the target before the hole closes (ms)
    WALK_STEP_TIME = 5000   # Interval at which we do walk steps (ms)
    RANK_STEP_TIME = 60000  # Interval at which we recalculate the scores of our peers (ms)

    def __init__(self, public_key, simulation, persistent_walking=False, directed_walking=False, alpha=0.1,
                 teleport_probability=0.5):
        self.public_key = public_key
        self.simulation = simulation
        self.live_edges = []
        self.node_directory = "nodes/" + base64.encodestring(str(self.public_key))
        if not os.path.exists(self.node_directory):
            os.makedirs(self.node_directory)
        self.block_database = Database(self.node_directory + "/multichain.db")
        self.log = open(self.node_directory + "/log.txt", 'w')

        self.directed_walking = directed_walking
        self.persistent_walking = persistent_walking

        if self.persistent_walking:
            self.teleport_probability = teleport_probability
            self.current_walk = None
            if self.directed_walking:
                self.walk_function = self.walk_statefull_directed
            else:
                self.walk_function = self.walk_statefull_undirected
        else:
            if self.directed_walking:
                self.walk_function = self.walk_stateless_directed
            else:
                self.walk_function = self.walk_stateless_undirected

        self.ranking = {}
        self.number_of_requests_received = 0
        self.alpha = alpha

    def receive_message(self, sender, message):
        message['function'](*message['arguments'])

    def send_message(self, target, message):
        self.simulation.send_message(self, target, message)

    def add_live_edge(self, peer):
        if peer not in self.live_edges:
            self.live_edges.append(peer)
            self.simulation.add_event(self.NAT_TIMEOUT_WITH_MARGIN, self.live_edge_timeout, [peer])

    # Only used for bootstrapping
    def send_identity(self, target):
        message = dict()
        message['function'] = target.receive_identity
        message['arguments'] = [self]
        self.send_message(target, message)

    # Only used for bootstrapping
    def receive_identity(self, sender):
        self.live_edges.append(sender)

    def add_blocks(self, blocks):
        self.block_database.add_blocks(blocks)
        self.log.write("Added " + str(len(blocks)) + " blocks to my database, I now have " +
                       str(self.block_database.get_number_of_blocks_in_db()) + " blocks\n")

    def take_walk_step(self):
        self.walk_function()
        self.simulation.add_event(self.WALK_STEP_TIME, self.take_walk_step)

    def walk_stateless_undirected(self):
        if self.live_edges:
            peer = random.choice(self.live_edges)
            self.send_introduction_request(peer)

    def walk_stateless_directed(self):
            peer = self.select_best_live_edge()
            self.send_introduction_request(peer)

    def walk_statefull_undirected(self):
        if self.current_walk:
            if random.random() <= self.teleport_probability:
                self.current_walk = random.choice(self.live_edges)
            else:
                self.current_walk = self.live_edges[-1]
        else:
            # Start walking
            self.current_walk = random.choice(self.live_edges)

        self.send_introduction_request(self.current_walk)

    def walk_statefull_directed(self):
        raise NotImplementedError

    def select_best_live_edge(self, exclude_peer=None):
        if self.live_edges:
            index = 0

            # Order the live edges:
            if self.ranking:
                ranked_live_edges = []
                for live_edge in self.live_edges:
                    if live_edge is exclude_peer:
                        continue
                    try:
                        rank = self.ranking[str(live_edge.public_key)][1]
                    except KeyError:
                        continue
                    ranked_live_edges.append((live_edge, rank))

                ranked_live_edges = sorted(ranked_live_edges, key=lambda x: x[1])
                if ranked_live_edges:
                    # Select an edge from the ranked live edges:
                    while random.random() > self.alpha:
                        index = (index + 1) % len(ranked_live_edges)

                    return ranked_live_edges[index][0]
            # It seems we can't rank our edges, so we just return a random one
            return random.choice(self.live_edges)

        else:
            print "I have no live edges"
            return None

    def update_ranking(self):
        self.ranking = get_ranking(self.block_database, self.public_key)
        self.simulation.add_event(self.RANK_STEP_TIME, self.update_ranking)

    def send_introduction_request(self, target):
        message = dict()
        message['function'] = target.receive_introduction_request
        message['arguments'] = [self]
        self.send_message(target, message)

    def receive_introduction_request(self, sender):
        self.add_live_edge(sender)  # This is know in dispersy as a stumble candidate
        self.send_introduction_response(sender)

    def send_introduction_response(self, target):
        if self.live_edges:
            if len(self.live_edges) == 1 and self.live_edges[0] == target:
                print "Can't introduce: I know only this peer"
            else:
                if self.directed_walking:
                    peer = self.select_best_live_edge(exclude_peer=target)
                else:
                    peer = None
                    while peer is None or peer == target:
                        peer = random.choice(self.live_edges)
                message = dict()
                message['function'] = target.receive_introduction_response
                message['arguments'] = [peer]
                self.send_message(target, message)
        else:
            print "I have no live edges"

    def receive_introduction_response(self, peer):
        self.add_live_edge(peer)
        self.send_crawl_request(peer)

    def live_edge_timeout(self, peer):
        self.live_edges.remove(peer)

    def send_crawl_request(self, target):
        message = dict()
        message['function'] = target.receive_crawl_request
        message['arguments'] = [self]
        self.send_message(target, message)

    def receive_crawl_request(self, sender):
        self.number_of_requests_received += 1
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

    def log_blocks(self, datafile):
        with open(datafile, 'a') as f:
            f.write(str(self.block_database.get_number_of_blocks_in_db()) + " ")

    def log_ranking(self, datafile):
        with open(datafile, 'a') as f:
            similarity = calculate_ranking_similarity(self.ranking, self.simulation.rankings[str(self.public_key)])
            f.write(str(similarity) + " ")

    def log_requests(self, datafile):
        with open(datafile, 'a') as f:
            f.write(str(self.number_of_requests_received) + "\n")
