import sys
import re
import itertools

# Return a frequent 1-itemset
def make_first_freq(dbs: list, sup: int) -> 'dict':
	freq = dict()
	for tx in dbs:
		for i in tx:
			if i in freq:
				freq[i] += 1
			else:
				freq[i] = 1
	for j in freq:
		if freq[j] < sup:
			del freq[j]
	return freq

# Return whether all the items in tuple are in a transcation
def tuple_in_db(tup: tuple, db: list) -> 'Bool':
	for i in range(len(tup)):
		if list(tup)[i] not in db:
			return False
	return True

# Return whether all the subsets of big tuple are in a small tuple
def subset_satisfy(tup: tuple, freq: dict, length: int) -> 'Bool':
	if length == 1:
		for comb in itertools.combinations(list(tup), length):
			if comb[0] not in freq:
				return False
		return True	
	else:
		for comb in itertools.combinations(list(tup), length):
			if comb not in freq:
				return False
		return True

# Make the frequent itemsets until there are no candidates
def apriori(dbs: list, sup: int, freqs: list):

	# Starting at making frequent 2-itemset
	length = 2
	
	# Initialize for further combinations
	list_for_comb = []
	for i in freqs[0]:
		list_for_comb.append(i)

	while True:
		new_freq = dict()
		ret = dict()
		candidate = []
	
		for comb in itertools.combinations(list_for_comb, length):
			if subset_satisfy(comb, freqs[length-2], length-1):
				tmp = set()
				for item in comb:
					tmp.add(item)
				candidate.append(tmp)

		# If no candidate is generated, stop the Apriori progress
		if len(candidate) == 0:
		   break

		for itemset in candidate:
			for tx in dbs:
				if tuple_in_db(itemset, tx):
					if tuple(itemset) in new_freq:
						new_freq[tuple(itemset)] += 1
					else:
						new_freq[tuple(itemset)] = 1

		# Remove the sets which don't satisfy the support
		for key in new_freq:
			if new_freq[key] >= sup:
				ret[key] = new_freq[key]
		freqs.append(ret)
		length += 1

# Return the values as a suggested form
def make_output_format(tu_1: tuple, tu_2: tuple, val_1: float, val_2: float) -> 'str':
	ret = '{'
	for item in tu_1:
		ret += str(item)
		if tu_1.index(item) != len(tu_1)-1:
			ret += ','
	ret += '}\t{'
	for item in tu_2:
		ret += str(item)
		if tu_2.index(item) != len(tu_2)-1:
			ret += ','
	ret += '}\t'+ '{}\t'.format(round(val_1, 2)) + '{}\n'.format(round(val_2, 2))
	return ret

# Print the results to an output file
def make_output(dbs: list, freqs: list, output_file_name: str):
	output = open(output_file_name, 'w')
	for output_len in range(1, len(freqs)):
		# When the length of associated itemset is 2
		if output_len == 1:
			for key in freqs[output_len]:
				first = key[0]
				second = key[1]
				third = (freqs[output_len][key] / 500)  * 100
				
				# Ordinary output
				conditional = 0
				for j in dbs:
					if first in j:
						conditional += 1
				fourth = (freqs[output_len][key] / conditional) * 100
				
				# Save as a suggested form
				line = '{' + '{}'.format(first) + '}\t' + '{' + '{}'.format(second) + '}\t' + '{}\t'.format(round(third, 2)) + '{}\n'.format(round(fourth, 2))
				output.write(line)

				# Reverse the previous output
				conditional = 0
				for j in dbs:
					if second in j:
						conditional += 1
				fourth = (freqs[output_len][key] / conditional) * 100
				
				# Save as a suggested form
				line = '{' + '{}'.format(second) + '}\t' + '{' + '{}'.format(first) + '}\t' + '{}\t'.format(round(third, 2)) + '{}\n'.format(round(fourth, 2))
				output.write(line)

		# When the length of associated itemset is more than 2
		else:
			for key in freqs[output_len]:
				list_for_comb = list(key)
				for select in range(1, int((len(key) / 2)) + 1):
					comb_first = itertools.combinations(list_for_comb, select)
					for first in comb_first:
						tmp = list_for_comb.copy()
						for j in range(len(first)):
							tmp.remove(first[j])
						second = tuple(tmp)
						third = (freqs[output_len][key] / 500) * 100
						
						# Ordinary output
						conditional = 0 
						for j in dbs:
							if tuple_in_db(first, j):
								conditional += 1
						fourth = (freqs[output_len][key] / conditional) * 100
						line = make_output_format(first, second, third, fourth)
						output.write(line)

						# Reverse the previous output
						conditional = 0 
						for j in dbs:
							if tuple_in_db(second, j):
								conditional += 1
						fourth = (freqs[output_len][key] / conditional) * 100
						line = make_output_format(second ,first, third, fourth)
						output.write(line)

	output.close()

if __name__ == "__main__":

	# Arrange the command line arguments
	min_sup_percent = sys.argv[1]
	input_file_name = sys.argv[2]
	output_file_name = sys.argv[3]

	datas = open(input_file_name, 'r')

	lines = datas.readlines()
	total_xs = len(lines)
	min_sup_times = float(min_sup_percent) * 0.01 * float(total_xs)

	dbs = [] # List of each transactions

	# Distinguish the numerical values from the input file
	for line in lines:
		tmp = re.findall('\d+', line)
		int_tmp = []
		for i in tmp:
			int_tmp.append(int(i))
		dbs.append(int_tmp)

	freqs = [] # List of dictionary(frequent (index)-itemset with support)
	freqs.append(make_first_freq(dbs, min_sup_times))
	apriori(dbs, min_sup_times, freqs)
	make_output(dbs, freqs, output_file_name)
	datas.close()
