import struct 

class BinaryReader(object):
	__slots__ = ["stream"]
	def __init__(self, stream):
		self.stream = stream
		# TODO build a bufferred stream
	
	def read(self, count):
		buf = self.stream.read(count)
		return buf
	
	def read8(self): return self.unpack(1,"B")
	def read16(self): return self.unpack(2, "!H")
	def read32(self): return self.unpack(4, "!I")
	def read64(self): return self.unpack(8, "!Q")

	def unpack(self, sz, t):
		buf = self.read(sz)
		(v,) = struct.unpack(t, buf)
		return v

class IgBinaryTypes(object):
	null = 0x00 # Null.

	ref8 = 0x01 # Array reference.
	ref16 = 0x02 # Array reference.
	ref32 = 0x03 # Array reference.

	bool_false = 0x04 # Boolean true.
	bool_true = 0x05 # Boolean false.

	long8p = 0x06 # Long 8bit positive.
	long8n = 0x07 # Long 8bit negative.
	long16p = 0x08 # Long 16bit positive.
	long16n = 0x09 # Long 16bit negative.
	long32p = 0x0a # Long 32bit positive.
	long32n = 0x0b # Long 32bit negative.

	double = 0x0c # Double.

	string_empty = 0x0d # Empty string.

	string_id8 = 0x0e # String id.
	string_id16 = 0x0f # String id.
	string_id32 = 0x10 # String id.

	string8 = 0x11 # String.
	string16 = 0x12 # String.
	string32 = 0x13 # String.

	array8 = 0x14 # Array.
	array16 = 0x15 # Array.
	array32 = 0x16 # Array.

	object8 = 0x17 # Object.
	object16 = 0x18 # Object.
	object32 = 0x19 # Object.

	object_id8 = 0x1a # Object string id.
	object_id16 = 0x1b # Object string id.
	object_id32 = 0x1c # Object string id.

	object_ser8 = 0x1d # Object serialized data.
	object_ser16 = 0x1e # Object serialized data.
	object_ser32 = 0x1f # Object serialized data.

	long64p = 0x20 # Long 64bit positive.
	long64n = 0x21 # Long 64bit negative.

	objref8 = 0x22 # Object reference.
	objref16 = 0x23 # Object reference.
	objref32 = 0x24 # Object reference.

	ref = 0x25 # Simple reference

class IgBinaryReader(BinaryReader):
	__slots__ = ["strings"]
	def __init__(self, stream):
		super(IgBinaryReader, self).__init__(stream)
		self.strings = []
		self.header()
	
	def header(self):
		version = self.read32()
		assert(version == 2)
	
	def readnull(self, t):
		return None
	
	def readbool(self, t):
		return (t == IgBinaryTypes.bool_true)
	
	def readlong(self, t):
		# note, all the long*p are even, long*n are odd
		multiplier = (t % 2) and -1 or 1
		if(t == IgBinaryTypes.long8p or t == IgBinaryTypes.long8n):
			i = self.read8()
		elif(t == IgBinaryTypes.long16p or t == IgBinaryTypes.long16n):
			i = self.read16()
		elif(t == IgBinaryTypes.long32p or t == IgBinaryTypes.long32n):
			i = self.read32()
		elif(t == IgBinaryTypes.long64p or t == IgBinaryTypes.long64n):
			i = self.read64()
		return multiplier * i
	
	def readdouble(self, t):
		return self.unpack(8, "!d")
	
	def readchararray(self, t):
		if(t == IgBinaryTypes.string8):
			c = self.read8()
		elif(t == IgBinaryTypes.string16):
			c = self.read16()
		elif(t == IgBinaryTypes.string32):
			c = self.read32()
		else:
			assert(0)

		s = self.read(c)
		self.strings.append(s)
		return s

	def readstringid(self, t):
		if(t == IgBinaryTypes.string_id8):
			k = self.read8()
		elif(t == IgBinaryTypes.string_id16):
			k = self.read16()
		elif(t == IgBinaryTypes.string_id32):
			k = self.read32()
		else:
			assert(0)
		
		return self.strings[k]
	
	def readstring(self, t):
		if(t == IgBinaryTypes.string_empty):
			return ""
		elif(t >= IgBinaryTypes.string8 and t <= IgBinaryTypes.string16):
			return self.readchararray(t)
		elif(t >= IgBinaryTypes.string_id8 and t <= IgBinaryTypes.string_id32):
			return self.readstringid(t)
		assert(0)

	def readarray(self, t):
		if(t == IgBinaryTypes.array8):
			c = self.read8()
		elif(t == IgBinaryTypes.array16):
			c = self.read16()
		elif(t == IgBinaryTypes.array32):
			c = self.read32()
		if(c == 0):
			return []

		keys = []
		values = []
		assoc = False

		for i in range(0, c):
			k = self.readvalue()
			values.append(self.readvalue())
			assoc = (assoc or type(k) != int)
			keys.append(k)

		if(assoc):
			retval = {}
		else:
			retval = []
			retval.extend([None]*c)

		mixed = zip(keys, values)
		for (k,v) in mixed:
			# zero indexed can also be sparse
			retval[k] = v
		return retval

	def readvalue(self):
		t = self.read8()
		if(t == IgBinaryTypes.null):
			return self.readnull(t)
		elif(t == IgBinaryTypes.bool_false or t == IgBinaryTypes.bool_true):
			return self.readbool(t)
		elif(t >= IgBinaryTypes.long8p and t <= IgBinaryTypes.long32n):
			return self.readlong(t)
		elif(t == IgBinaryTypes.long64p or t == IgBinaryTypes.long64n):
			return self.readlong(t)
		elif(t == IgBinaryTypes.double):
			return self.readdouble(t)
		elif(t >= IgBinaryTypes.string_empty and t <= IgBinaryTypes.string32):
			return self.readstring(t)
		elif(t >= IgBinaryTypes.array8 and t <= IgBinaryTypes.array32):
			return self.readarray(t)
		else:
			assert(0)

if __name__ == "__main__":
	ig = IgBinaryReader(open("array.ig"))
	print ig.readvalue()
