#!/usr/bin/python

import argparse

from simulation import Simulation

parser = argparse.ArgumentParser(description='Simulate a run of the multichain walker.')
parser.add_argument('-t', '--time', default=1000, help='Time to run the simulation for in miliseconds', type=int)
parser.add_argument('-f', '--file', default='nodes/results.dat', help='Output file for the simulation')
parser.add_argument('-v', '--verbose', default=False, help='Enable verbose output', type=bool)

args = parser.parse_args()

Simulation(args.time, args.file, args.verbose).start()
