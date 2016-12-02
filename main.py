#!/usr/bin/python

import argparse

from simulation import Simulation

parser = argparse.ArgumentParser(description='Simulate a run of the multichain walker.')
parser.add_argument('-t', '--time', default=1000, help='Time to run the simulation for in miliseconds', type=int)
parser.add_argument('-d', '--dir', default='plot', help='Output directory for the simulation')
parser.add_argument('-v', '--verbose', default=False, help='Enable verbose output', type=bool)
walker_types = ['state-less undirected', 'state-less directed', 'state-full undirected', 'state-full directed']
parser.add_argument('-w', '--walker', default='state-less undirected', help='The type of walker used',
                    choices=walker_types)
parser.add_argument('-b', '--block_limit', default=None, help='The number of blocks to be used for the simulation,'
                                                              ' starting from the oldest blocks', type=int)
args = parser.parse_args()

Simulation(args.time, args.dir, args.verbose, args.walker, args.block_limit).start()
