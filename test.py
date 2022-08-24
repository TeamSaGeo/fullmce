def findErrorNums(nums):
	result = []
	doublon =  []
	for i,elt in enumerate(nums):
		if elt not in doublon:
			doublon.append(elt)
		else:
			result.append(elt)
			result.append(elt+1)
	return result


if __name__ == '__main__':
	line = input()
	components = line.strip().split()
	components = [int(component) for component in components]

	print(findErrorNums(components))
