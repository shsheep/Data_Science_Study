import sys
import re
import math
import collections

class DecisionTree:
	def __init__(self, parent_attr, value, inheritance):
		self.parent = parent_attr
		self.attr = value
		self.inherit = inheritance
		self.children = []

	def appendChild(self, child):
		self.children.append(child)

	def printTree(self, depth: int):
		print(depth)
		print('Parent is', self.parent)
		print('Attribute is', self.attr)
		print('Inheritance is', self.inherit)
		if self.children:
			print('Children is')
			for child in self.children:
				child.printTree(depth+1)
	
# For train
def InformationGain(dbs: list, attrs: list, attr_set: list, exceptions: list):
	gains = [0] * len(attrs)

	# Calculate each Information Gains
	class_count = collections.defaultdict(lambda: 0)
	for tup in dbs:
		if tup[1]:
			class_count[tup[0][-1]] += 1

	## Calculate the original entropy
	each_number = []
	key_list = list(class_count)
	total_number = 0
	for key in key_list:
		each_number.append(class_count[key])
		total_number += class_count[key]
	origin_entropy = 0
	for i in range(len(each_number)):
		each_number = class_count[key_list[i]]
		each_prob = each_number / total_number
		origin_entropy -= each_prob * math.log(each_prob, 2)
	
	## Prepare to count each attribute values with class label
	attr_count_list = []
	for idx in range(len(attr_set)):#attr_group in attr_set:
		attr_count = dict() # defaultdict and lambda initialize?
		tmp = list(attr_set[idx])
		for item in tmp:
			tmp_dict = dict()
			for key in key_list:
				tmp_dict[key] = 0
			attr_count[(attrs[idx], item)] = tmp_dict
		attr_count_list.append(attr_count)
		
	for tup in dbs:
		if tup[1]:
			for idx in range(len(tup[0])):
				if attrs[idx] in exceptions:
					continue
				else:
					attr_count_list[idx][(attrs[idx], tup[0][idx])][tup[0][-1]] += 1
	# print(attr_count_list)	
	## Calculate the divided entropy
	for idx in range(len(gains)):
		divided_entropy = 0
		for col in attr_count_list[idx]:
			cont_flag = False
			if col[0] in exceptions:
				continue
			if attrs[idx] == col[0]:
				local_each_number = []
				for key in key_list:
					local_label = attr_count_list[idx][col][key]
					if local_label == 0:
						cont_flag = True
						continue
					local_each_number.append(local_label)

				if cont_flag:
					continue
				else:
					local_total = sum(local_each_number)
					local_each_prob = []
					for number in local_each_number:
						prob = number / local_total
						local_each_prob.append(prob)
					for prob in local_each_prob:
						divided_entropy -= (local_total / total_number) * (prob * math.log(prob, 2))

		gains[idx] = origin_entropy - divided_entropy
	
	# Exclude the class label column
	gains[-1] = -100
	for attr in exceptions:
		gains[attrs.index(attr)] = -100
	return gains, attr_count_list


def GainRatio(dbs: list, gains: list, attrs: list, attr_count_list: list):
	split_infos = [0] * len(attrs)
	
	class_count = collections.defaultdict(lambda: 0)
	for tup in dbs:
		if tup[1]:
			class_count[tup[0][-1]] += 1

	each_number = []
	key_list = list(class_count)
	total_number = 0
	for key in key_list:
		each_number.append(class_count[key])
		total_number += class_count[key]

	## Calculate the numbers
	yes_number = class_count['yes']
	no_number = class_count['no']
	for idx in range(len(split_infos)):
		for col in attr_count_list[idx]:
			if col[0] == attrs[idx]:
				local_total = attr_count_list[idx][col]['yes'] + attr_count_list[idx][col]['no']
				if local_total == 0:
					continue
				split_infos[idx] -= (local_total / total_number) * math.log(local_total / total_number, 2)
	
	gain_ratio = [0] * len(attrs)
	for idx in range(len(gains)):
		if split_infos[idx] == 0:
			continue
		gain_ratio[idx] = gains[idx]/split_infos[idx]
	# Exclude the class label column and exceptions
	gain_ratio[-1] = -100
	#for attr in exceptions:
	#	GainRatio[attrs.index(attr)] = -100
	return gain_ratio

def ConstructDT(dbs: list, attrs: list, dt: DecisionTree, exceptions: list, class_labels_count: dict):
	# 
	class_count = collections.defaultdict(lambda: 0)
	for tup in dbs:
		if tup[1]:
			class_count[tup[0][-1]] += 1
	each_number = []
	key_list = list(class_count)
	for key in key_list:
		each_number.append(class_count[key])

	# DEBUGGING SECTION #
	#print('================================')
	#for tup in dbs:
	#	print(tup)
	#print(exceptions)
	#print('key list is', key_list)
	#print('each number is', each_number)
	
	
	# Termination Condition 1 : All samples belong to the same class OR there are no samples left 
	if each_number.count(0) == len(each_number) - 1:
		dt.inherit = key_list[0]
		class_labels_count[dt.inherit] += 1
		return
	else:
	# Termination Condition 2 : All attributes are already considered to make current sub decision tree
		all_attr_in = True
		for attr in attrs[:-1]:
			if attr not in exceptions:
				all_attr_in = False
				break
		if all_attr_in:
			if each_number:
				dt.inherit = key_list[each_number.index(min(each_number))]

			# Very Special Exception Case. . . 
			else:
				not_in = 0
				for key in list(class_labels_count):
					if class_labels_count[key] == 0:
						not_in = key
						break
				#print('UNKNOWN')
				dt.inherit = not_in
				class_labels_count[dt.inherit] += 1
			return

		# Get the maximum Gain or Gain Ratio attribute
		gains, attr_count_list = InformationGain(dbs, attributes, attr_set, exceptions)

		# DEBUGING SECTION #
		#gain_ratio = GainRatio(dbs, gains, attributes, attr_count_list)
		#print('gains', gains)
		#print('gain_ratio', gain_ratio)
		max_gain_idx = 0
		for idx in range(1, len(gains)):
			if attr[max_gain_idx] in exceptions:
				max_gain_idx = idx
			if gains[max_gain_idx] < gains[idx] and attr[idx] not in exceptions:
				max_gain_idx = idx
		
		# Using Information Gain,
		exceptions.append(attrs[max_gain_idx])
		print(exceptions)
		# If root,
		if dt.parent == None:
			dt.inherit = attrs[max_gain_idx]
			class_labels_count[dt.inherit] += 1
			for value in list(attr_set)[max_gain_idx]:
				child = DecisionTree(dt.inherit, value, None)
				dt.appendChild(child)
			for child in dt.children:
				#print(max_gain_idx, child.attr)
				tmp_dbs = ModifyDB(dbs, max_gain_idx, child.attr)
				exceptions_tmp = exceptions.copy()
				class_labels_count_tmp = class_labels_count.copy()
				ConstructDT(tmp_dbs, attrs, child, exceptions_tmp, class_labels_count_tmp)
			# Add child node
			# And iterate the children using recursive
		else:
			dt.inherit = attrs[max_gain_idx]
			for value in list(attr_set)[max_gain_idx]:
				child = DecisionTree(dt.inherit, value, None)
				dt.appendChild(child)
			for child in dt.children:
				#print(max_gain_idx, child.attr)
				tmp_dbs = ModifyDB(dbs, max_gain_idx, child.attr)
				exceptions_tmp = exceptions.copy()
				class_labels_count_tmp = class_labels_count.copy()
				ConstructDT(tmp_dbs, attrs, child, exceptions_tmp, class_labels_count_tmp)
				
		return dt

# Collect datas which  have specific attribute value
def ModifyDB(dbs: list, attr_idx: int, value: str):
	ret = dbs.copy()
	for idx in range(len(ret)):#tup in ret:
		if ret[idx][0][attr_idx] != value:
			ret[idx] = (ret[idx][0], False)
	return ret

def DetermineClass(tx: list, attrs: list, dt: DecisionTree):
	if not dt.children:
		#print(dt.inherit)
		return dt.inherit
	else:
		for child in dt.children:
			if tx[attrs.index(dt.inherit)] == child.attr:
				return DetermineClass(tx, attrs, child)

if __name__ == "__main__":
	train_file_name = sys.argv[1]
	test_file_name = sys.argv[2]
	output_file_name = sys.argv[3]

	train_datas = open(train_file_name, 'r')

	lines = train_datas.readlines()
	attributes = lines[0].split()

	dbs = []
	attr_set = []
	for attr in attributes:
		attr_set.append(set())

	for line in lines[1:]:
		tx = line.split()
		dbs.append((tx, True))
		for idx in range(len(tx)):
			attr_set[idx].add(tx[idx])

	class_labels = list(attr_set[-1])
	class_labels_count = collections.defaultdict(lambda: 0)
	for label in class_labels:
		class_labels_count[label] = 0
	exceptions = []	

	dt = DecisionTree(None, None, None)
	ConstructDT(dbs, attributes, dt, exceptions, class_labels_count)
	# Print the whole Decision Tree
	#dt.printTree(0)
	
	test_file = open(test_file_name, 'r')
	test_lines = test_file.readlines()
	test_dbs = []
	for line in test_lines[1:]:
		tx = line.split()
		test_dbs.append(tx)
	
	output_file = open(output_file_name, 'w')
	for attr in attributes:
		output_file.write(attr + '\t')
	output_file.write('\n')
	for tx in test_dbs:
		for value in tx:
			output_file.write(value + '\t')
		output_file.write(DetermineClass(tx, attributes, dt))
		output_file.write('\n')
	
	test_file.close()
	train_datas.close()
	output_file.close()
