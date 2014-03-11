import collections
from cache import Cache

""" Stores the statistics of a single cache. """
class Statistics:
	def __init__(self, cache):
		self.cache = cache
		self.write_hits = 0.0
		self.write_misses = 0.0
		self.read_hits = 0.0
		self.read_misses = 0.0

		self._invalidations = 0.0
		self._private_accesses = 0.0
		self._shared_read_only_accesses = 0.0

	@property
	def writes(self):
	  return self.write_hits + self.write_misses

	@property
	def reads(self):
		return self.read_hits + self.read_misses

	@property
	def hits(self):
	  return self.write_hits + self.read_hits

	@property
	def misses(self):
	  return self.write_misses + self.read_misses

	@property
	def accesses(self):
	  return self.hits + self.misses

	@property
	def invalidations(self):
	    return self._invalidations

	@property
	def private(self):
	  return self._private_accesses
	
	@property
	def shared_read(self):
	  return self._shared_read_only_accesses
	
""" Tracker object responsible for registering 
		write/read hits and misses. """
class Tracker(object):

	def __init__(self):
		self.caches = {}

	def add_cache(self, cache):
		self.caches[cache.cache_id] = Statistics(cache)

	def register_write_hit(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics.write_hits += 1

	def register_write_miss(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics.write_misses += 1

	def register_read_hit(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics.read_hits += 1

	def register_read_miss(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics.read_misses += 1

	def register_invalidation(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics.invalidations += 1

	def register_private_access(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics._private_accesses += 1

	def register_shared_read_only_access(self, cache_id, address):
		cache_statistics = self.caches[cache_id]
		cache_statistics._shared_read_only_accesses += 1

	""" Fills the dictionary with all the necessary statistics
			for printing it out on the command line. """
	def get_per_cache_stats(self, cache_id):
		cache_statistics = self.caches[cache_id]

		stats = {}

		stats["accesses"] = cache_statistics.accesses

		stats["writes"] = cache_statistics.writes
		stats["reads"] = cache_statistics.reads

		stats["hits"] = cache_statistics.hits
		stats["misses"] = cache_statistics.misses

		stats["write_misses"] = cache_statistics.write_misses
		stats["read_misses"] = cache_statistics.read_misses

		stats["invalidations"] = cache_statistics.invalidations
		stats["private"] = cache_statistics.private
		stats["shared_read"] = cache_statistics.shared_read

		return stats




	