#!/usr/bin/python

import argparse

from simulation import Simulation

parser = argparse.ArgumentParser(description='Simulate a run of the multichain walker.')
parser.add_argument('-t', '--time', default=5000, help='Time to run the simulation for in miliseconds', type=int)
parser.add_argument('-f', '--file', default='nodes/results.dat', help='Output file for the simulation')
parser.add_argument('-v', '--verbose', default=False, help='Enable verbose output', type=bool)
parser.add_argument('-n', '--nat', default=0, help='Percentage of peers that is behind a NAT', type=int)

args = parser.parse_args()

Simulation(args.time, args.file, args.verbose, args.nat).start()
