import sys
import numpy as np
import collections

if __name__ == "__main__":
	train_file_name = sys.argv[1]
	test_file_name = sys.argv[2]

	train_datas = open(train_file_name, 'r')

	lines = train_datas.readlines()
	for_num_users = lines[-1].split()
	num_users = int(for_num_users[0])

	users = []
	for i in range(num_users+1):
		tmp = collections.defaultdict(lambda: 0)
		users.append(tmp)
	for line in lines:
		tmp = line.split()
		user_idx = int(tmp[0])
		item_idx = int(tmp[1])
		users[user_idx][item_idx] = int(tmp[2])
	#for dic in users:
	#	print(dic)


#	for idx in range(cluster_number):
#		file_name = input_file_name[:6] + '_cluster_' + str(idx) + '.txt'
#		output_file = open(file_name, 'w')
#		for obj in results[len_results[idx][1]]:
#			output_file.write(obj)
#			output_file.write('\n')

	train_datas.close()
#	output_file.close()
