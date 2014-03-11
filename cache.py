""" A representation of the processor caches, using the
		3-state MSI cache coherence protocol. """

from cache_line import CacheLine
import collections
import math

""" Enumeration of the 3 MSI states. """
class State():
	INVALID = 0
	MODIFIED = 1
	SHARED = 2

""" A cache line representation.
		Holds all the state data. """
class CacheLine(object):
	def __init__(self):
		self.tag = None # We get the tag from the address
		self._state = None # Don't assume any initial state
		self._written_to = False

	@property
	def state(self):
	  return self._state
	@state.setter
	def state(self, value):
	  self._state = value

	@property
	def written_to(self):
	    return self._written_to
	@written_to.setter
	def written_to(self, value):
	    self._written_to = value
	

""" A cache representation. Each cache has its own ID and
		is connected to the bus, as well as to the tracker. """
class Cache(object):
	def __init__(self, cache_id, lines, line_size, bus, statistics_tracker, verbose):
		self.cache_id = cache_id
		self.bus = bus
		self.bus.add_cache(self)
		self.statistics_tracker = statistics_tracker
		self.statistics_tracker.add_cache(self)
		self.verbose = verbose

		if not (multiple_of_two(lines) or not multiple_of_two(line_size)):
			raise ValueError("The number of lines and the line size must both be multiples of two!")

		# Store cache block as bits 
		# We need this to get the tag, index and offset of a cache block
		self.block = int(math.log(lines, 2))
		# The offset size
		self.block_offset = int(math.log(line_size, 2))

		# defaultdict automatically maps the first encounter of a key to a cache line
		self.all_cache_lines = collections.defaultdict(CacheLine)

	""" Simulates a write to a block. """
	def write_to_address(self, address):
		tag, block_id, _ = self.get_block(address)
		cache_block = self.all_cache_lines[block_id]
		miss_type = "w"
		
		if self.verbose:
			print "A write by processor %s to address %s." % (self.cache_id, address)

		# The block is invalid or shared - Write miss
		if (cache_block.state == State.INVALID or 
				cache_block.state == State.SHARED or 
				cache_block.tag != tag):
			self.statistics_tracker.register_write_miss(self.cache_id, address)
			self.bus.propagate_miss(self.cache_id, address, miss_type)
			if self.verbose:
				print "A write miss by processor %s to address %s." % (self.cache_id, address)

			cache_block.state = State.MODIFIED
			cache_block.tag = tag
			cache_block.written_to = True
			return False

		# The block is in modified state - Hit
		else:
			self.statistics_tracker.register_write_hit(self.cache_id, address)
			self.statistics_tracker.register_private_access(self.cache_id, address)
			self.bus.propagate_invalidation(self.cache_id, address) # Invalidate all but the local state
			self.statistics_tracker.register_invalidation(self.cache_id, address)

			if self.verbose:
				print "A write hit by processor %s to address %s." % (self.cache_id, address)

			cache_block.state = cache_block.state # Update the local cache state
			return True

	""" Simulates a read to a block. """
	def read_from_address(self, address):
		tag, block_id, _ = self.get_block(address)
		cache_block = self.all_cache_lines[block_id]
		miss_type = "r"

		if self.verbose:
			print "A read by processor %s to address %s." % (self.cache_id, address)

		# If the state is invalid - Read miss
		if (cache_block.state == State.INVALID or 
				cache_block.tag != tag):
			self.statistics_tracker.register_read_miss(self.cache_id, address)
			self.bus.propagate_miss(self.cache_id, address, miss_type)

			if self.verbose:
				print "A read miss by processor %s to address %s." % (self.cache_id, address)

			cache_block.state = State.SHARED
			cache_block.tag = tag
			cache_block.written_to = False
			return False

		# In case of a shared or modified state = Read hit
		elif (cache_block.state == State.SHARED or 
					cache_block.state == State.MODIFIED):
			if self.verbose:
				print "A read hit by processor %s to address %s." % (self.cache_id, address)
			self.statistics_tracker.register_read_hit(self.cache_id, address)
		
			# Shared read-only
			if (cache_block.state == State.SHARED 
					and cache_block.written_to == False):
				self.statistics_tracker.register_shared_read_only_access(self.cache_id, address)

			# Private data access
			if cache_block.state == State.MODIFIED:
				self.statistics_tracker.register_private_access(self.cache_id, address)
			
			cache_block.state = cache_block.state
			return True

	""" Updates the state of a block on a write miss. """
	def handle_write_miss(self, address):
		tag, block_id, _ = self.get_block(address)
		cache_block = self.all_cache_lines[block_id]
		
		if cache_block.state != State.INVALID and cache_block.tag == tag: 
			cache_block.state = State.INVALID

	""" Updates the state of a block on a read miss. """
	def handle_read_miss(self, address):
		tag, block_id, _ = self.get_block(address)
		cache_block = self.all_cache_lines[block_id]

		if cache_block.state == State.MODIFIED and cache_block.tag == tag:
			cache_block.state = State.SHARED

	""" Handles write invalidations. """
	def handle_invalidation(self, address):
		tag, block_id, _ = self.get_block(address)
		cache_block = self.all_cache_lines[block_id]
		cache_block.state = State.INVALID

	""" Splits address into its tag, index and offset 
			parts to retrieve the details of the cache block. """
	def get_block(self, address):
		# Offset is in the last bits of the block
		offset_mask = (1 << self.block_offset) - 1
		offset = address & offset_mask

		# The index describing which cache line the data is in
		index_mask = (1 << (self.block + self.block_offset)) - 1
		index = (address & index_mask) >> self.block_offset
		
		# The tag is at the beginning of the block
		tag_mask = ~index_mask
		tag = (address & tag_mask) >> (self.block + self.block_offset)

		return tag, index, offset

""" Check if a number is a multiple of 2. """
def multiple_of_two(value):
	return ((value & (value - 1)) == 0) and value > 0