from cache import *
from tracker import Tracker
from bus import Bus
import argparse

""" Simulate the behavior of a set of caches with a shared bus,
		based on a trace file input. """ 
class Simulator(object):

	def __init__(self, lines, line_size, verbose):
		self.statistics_tracker = Tracker()
		self.processors = 4
		self.verbose = verbose

		shared_bus = Bus()

		# Register one cache for each processor
		self.caches = []
		for cache_id in range(self.processors):
			cache = Cache(cache_id, lines, line_size, shared_bus, 
										self.statistics_tracker, self.verbose)
			self.caches.append(cache)

	""" Parse a trace file and simulate its contents. """
	def parse_and_simulate(self, trace_file):
		for line in trace_file:
			split_line = line.split()
			# Split the line to determine the id, access type and address
			cache_id = int(split_line[0][1:])
			access_type = split_line[1]
			address = int(split_line[2])

			if access_type == "W":
				self.caches[cache_id].write_to_address(address)
			elif access_type == "R":
				self.caches[cache_id].read_from_address(address)
			else:
				print "Unknown access type. Continuing with next line."
				continue

		trace_file.close()

	""" Track and report the statistics of the simulation. 
			(It's a bit of a mess with all the print statements, 
			and it does screw up piping of the output, but I went 
			for the, in the terminal, eye-pleasing solution =)) """			
	def print_statistics(self):
		# ANSI color codes for command line output
		header_format = "\x1B[\033[1;31m"
		variable_format = "\x1B[\033[35m"
		unformat = "\x1B[0m"

		for cache in self.caches:
			cache_statistics = self.statistics_tracker.get_per_cache_stats(cache.cache_id)

			# Get all the stats from the tracker
			accesses = cache_statistics["accesses"]

			writes = cache_statistics["writes"]
			reads = cache_statistics["reads"]

			misses = cache_statistics["misses"]
			write_misses = cache_statistics["write_misses"]
			read_misses = cache_statistics["read_misses"]

			invalidations = cache_statistics["invalidations"]
			private = cache_statistics["private"]
			shared_read = cache_statistics["shared_read"]
			shared_read_write = accesses - (private + shared_read)

			print "-" * 20
			print header_format + "PROCESSOR " + str(cache.cache_id) + unformat
			print "-" * 20
			print variable_format + "Accesses: " + unformat + str(int(accesses))
			print variable_format + "Writes: " + unformat + str(int(writes))
			print variable_format + "Reads: " + unformat + str(int(reads)) + "\n"

			print variable_format + "Misses: " + unformat + str(int(misses))
			print variable_format + "Write misses: " + unformat + str(int(write_misses))
			print variable_format + "Read misses: " + unformat + str(int(read_misses))
			print variable_format + "Invalidations: " + unformat + str(int(invalidations))
			print variable_format + "Miss rate: " + unformat + self.calculate_rate(misses, accesses)
			print variable_format + "Write miss rate: " + unformat + self.calculate_rate(write_misses, writes)
			print variable_format + "Read miss rate: " + unformat + self.calculate_rate(read_misses, reads) + "\n"

			print variable_format + "Private accesses: " + unformat + str(int(private))
			print variable_format + "Shared read-only accesses: " + unformat + str(int(shared_read))
			print variable_format + "Shared read-write accesses: " + unformat + str(int(shared_read_write))
			print variable_format + "Private access rate: " + unformat + self.calculate_rate(private, accesses)
			print variable_format + "Shared read-only rate: " + unformat + self.calculate_rate(shared_read, accesses)
			print variable_format + "Shared read-write rate: " + unformat + self.calculate_rate(shared_read_write, accesses) + "\n"

	""" Calculates rate percentages. """
	def calculate_rate(self, value_one, value_two):
		try:
			rate = value_one / value_two
		except ZeroDivisionError:
			rate = 0

		rate_as_string = "{0:.4f}".format(rate)
		return rate_as_string

""" Parse the command line arguments and run the simulation. """
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-l", default=1024, dest="lines",
											help="The number of cache lines (Default = 1024).", type=int)
	parser.add_argument("-s", default=64 ,dest="line_size",
											help="The size of each cache line (Default = 64).", type=int)
	parser.add_argument("-v", action="store_true", default=False, dest="verbose",
											help="Turn on to output simulation in terminal, line-by-line.")
	parser.add_argument('trace_file', type=argparse.FileType('r'))

	args = parser.parse_args()

	"""Create a new simulator with the number of cache lines,
	 		line size and verbose boolean as arguments, then run it. """
	simulation = Simulator(args.lines, args.line_size, args.verbose)
	simulation.parse_and_simulate(args.trace_file)
	
	print "-" * 20
	print "GENERAL INFORMATION"
	print "-" * 20
	print "Number of lines: " + str(args.lines)
	print "Line size: " + str(args.line_size) + "\n"
	simulation.print_statistics()
	print "\x1B[\033[32m" "Simulation finished!" + "\x1B[0m" + "\n"

" Call the main method. "
if __name__ == "__main__":
	main()