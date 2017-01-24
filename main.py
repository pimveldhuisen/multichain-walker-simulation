#!/usr/bin/python

import argparse

from simulation import Simulation

parser = argparse.ArgumentParser(description='Simulate a run of the multichain walker.')
parser.add_argument('-t', '--time', default=1000, help='Time to run the simulation for in miliseconds', type=int)
parser.add_argument('-d', '--dir', default='plot', help='Output directory for the simulation')
parser.add_argument('-v', '--verbose', default=False, help='Enable verbose output', type=bool)
parser.add_argument('-pw', '--persistent_walking', default=False, help='Toggle persistent walking', action='store_true')
parser.add_argument('-dw', '--directed_walking', default=False, help='Toggle directed walking', action='store_true')
parser.add_argument('-b', '--block_limit', default=None, help='The number of blocks to be used for the simulation,'
                                                              ' starting from the oldest blocks', type=int)
parser.add_argument('-a', '--alpha', default=0.1, help='The alpha factor used for the directed walking algorithm',
                    type=float)
args = parser.parse_args()

Simulation(args.time, args.dir, args.verbose, args.persistent_walking, args.directed_walking, args.block_limit,
           args.alpha).start()
