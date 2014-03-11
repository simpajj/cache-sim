""" A representation of the system bus. 
		It stores all the caches and uses helper methods in 
		the cache class to propagate misses and invalidations. """

class Bus(object):
	def __init__(self):
		self.all_caches = []

	def add_cache(self, cache):
		self.all_caches.append(cache)

	""" Propagate misses to all caches updating the states
			of their local copies. """
	def propagate_miss(self, cache_id, address, miss_type):
		for cache in self.all_caches:
			if cache.cache_id != cache_id:
				if miss_type == "r":
					cache.handle_read_miss(address)
				else:
					cache.handle_write_miss(address)

	""" Invalidate the data in all caches in the
			case of a write hit. Write invalidation. """
	def propagate_invalidation(self, cache_id, address):
		for cache in self.all_caches:
			if cache.cache_id != cache_id:
				cache.handle_invalidation(address)


