import sys

def Distance(pt1, pt2):
	return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])** 2)**0.5

if __name__ == "__main__":
	input_file_name = sys.argv[1]
	cluster_number = int(sys.argv[2])
	eps = float(sys.argv[3])
	minpts = int(sys.argv[4])

	input_datas = open(input_file_name, 'r')

	lines = input_datas.readlines()
	objects =[]
	for line in lines:
		tmp = line.split()
		tmp.append(False)
		objects.append(tmp)
	
	results = []
	core_points = []
	for ob_1 in objects:
		flag_combine = False
		tmp = [ob_1[0]]
		for ob_2 in objects:
			if ob_2[0] == ob_1[0]:
				continue
			if Distance((float(ob_1[1]), float(ob_1[2])), (float(ob_2[1]), float(ob_2[2]))) <= eps:
				tmp.append(ob_2[0])

		if len(tmp) < minpts:
			continue

		for idx in range(len(results)):
			if ob_1[0] in results[idx]:
				flag_combine = True
				break

		if flag_combine:
			results[idx] += tmp
			results[idx] = list(set(results[idx]))
			core_points[idx].append(ob_1[0])
		else:
			results.append(tmp)
			core_points.append([ob_1[0]])

	len_results = []
	for idx in range(len(results)):
		len_results.append((len(results[idx]), idx))
	len_results.sort(key = lambda element : element[0], reverse=True)

	#for res in results:
	#	print('=============================================')
	#	print(res)
	
	for idx in range(cluster_number):
		file_name = input_file_name[:6] + '_cluster_' + str(idx) + '.txt'
		output_file = open(file_name, 'w')
		for obj in results[len_results[idx][1]]:
			output_file.write(obj)
			output_file.write('\n')

	input_datas.close()
	output_file.close()
