
import math
import hashlib
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from cola.core.bloomfilter.hashtype import HashType


default_hashbits = 96

class HashType(object):
    def __init__(self, value='', hashbits=default_hashbits, hash_=None):
        "Relies on create_hash() provided by subclass"
        self.hashbits = hashbits
        if hash_:
            self.hash = hash_
        else:
            self.create_hash(value)

    def __trunc__(self):
        return self.hash

    def __str__(self):
        return str(self.hash)
    
    def __long__(self):
        return long(self.hash)

    def __float__(self):
        return float(self.hash)
        
    def __cmp__(self, other):
        if self.hash < long(other): return -1
        if self.hash > long(other): return 1
        return 0
    
    def hex(self):
        return hex(self.hash)

    def hamming_distance(self, other_hash):
        x = (self.hash ^ other_hash.hash) & ((1 << self.hashbits) - 1)
        tot = 0
        while x:
            tot += 1
            x &= x-1
        return tot

class BloomFilter(HashType):
    def __init__(self, value='', capacity=30000, false_positive_rate=0.01):
        """
        'value' is the initial string or list of strings to hash,
        'capacity' is the expected upper limit on items inserted, and
        'false_positive_rate' is self-explanatory but the smaller it is, the larger your hashes!
        """
        self.create_hash(value, capacity, false_positive_rate)

    def create_hash(self, initial, capacity, error):
        """
        Calculates a Bloom filter with the specified parameters.
        Initalizes with a string or list/set/tuple of strings. No output.

        Reference material: http://bitworking.org/news/380/bloom-filter-resources
        """
        self.hash = 0L
        self.hashbits, self.num_hashes = self._optimal_size(capacity, error)

        if len(initial):
            if type(initial) == str:
                self.add(initial)
            else:
                for t in initial:
                    self.add(t)
    
    def _hashes(self, item):
        """
        To create the hash functions we use the SHA-1 hash of the
        string and chop that up into 20 bit values and then
        mod down to the length of the Bloom filter.
        """
        m = hashlib.sha1()
        m.update(item)
        digits = m.hexdigest()
    
        # Add another 160 bits for every 8 (20-bit long) hashes we need
        for i in range(self.num_hashes / 8):
            m.update(str(i))
            digits += m.hexdigest()
    
        hashes = [int(digits[i*5:i*5+5], 16) % self.hashbits for i in range(self.num_hashes)]
        return hashes  

    def _optimal_size(self, capacity, error):
        """Calculates minimum number of bits in filter array and
        number of hash functions given a number of enteries (maximum)
        and the desired error rate (falese positives).
        
        Example:
            m, k = self._optimal_size(3000, 0.01)   # m=28756, k=7
        """
        m = math.ceil((capacity * math.log(error)) / math.log(1.0 / (math.pow(2.0, math.log(2.0)))))
        k = math.ceil(math.log(2.0) * m / capacity)
        return (int(m), int(k))

    
    def add(self, item):
        "Add an item (string) to the filter. Cannot be removed later!"
        for pos in self._hashes(item):
            self.hash |= (2 ** pos)

    def __contains__(self, name):
        "This function is used by the 'in' keyword"
        retval = True
        for pos in self._hashes(name):
            retval = retval and bool(self.hash & (2 ** pos))
        return retval