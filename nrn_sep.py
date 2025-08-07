import os 
# input_file = 'test_retinal_cells.swc' # replace with your SWC file path
# output_path = 'C:\\Users\\emanu\\USC-Summer\\nrn_sep_files'  # replace with your desired output directory

def main(input_file, output_path): 
    """
    Main function to separate neurons based on SWC data.
    :param input_file: Path to the input SWC file.
    :param output_path: Path to save the output files.
    """
    import sys
    from swcToolkit import swcToolkit  # Import the SWC toolkit
    # import os  # Import os for file operations
    file_name = os.path.splitext(input_file)[0]
    orphan_file = 'orphan'
    swc = swcToolkit() # load swc tool kit for use throughout
    swc_data = swc.read_swc_file(input_file)  # Read SWC data
    recursion_limit = len(swc_data) + 1 # changes the recursion limit so that recursive function can be called more than 5 times.
    sys.setrecursionlimit(recursion_limit)

    soma_indices = soma_id_and_orphan(swc_data) # array of soma indices from swc data
    dictionary_data = data_into_dictionary(swc_data) # 
    num_soma = 0
    returned_nodes = 0
    sample_col = 0
    num_orphans = 0
    r_orphan_nodes = 0

    # Separate neurons based on soma indices and export
    for idx in range(len(soma_indices[0])): 
        num_nodes = 0
        iteration = 1
        tree = {1: [swc_data[idx][sample_col]]}
        new_tree = soma_tree(tree, iteration, dictionary_data, num_nodes)
        # temp_data = sep_nrn(swc_data, idx)
        # print("Number of nodes separated: ", new_tree[1])
        unfiltered_nrn_data = data_idx_to_data(swc_data, new_tree[0])
        returned_nodes += new_tree[1]
        nrn_data = redef_idx(unfiltered_nrn_data)
        num_soma += 1 
        file(nrn_data, output_path, num_soma, file_name)  # Write se parated neurons to files
        print(returned_nodes, 'nodes separated.\n')

    for idx in range(len(soma_indices[1])): 
        num_nodes = 0
        iteration = 1
        tree = {1: [swc_data[idx][sample_col]]}
        new_tree = soma_tree(tree, iteration, dictionary_data, num_nodes)
        # temp_data = sep_nrn(swc_data, idx)
        # print("Number of nodes separated: ", new_tree[1])
        unfiltered_nrn_data = data_idx_to_data(swc_data, new_tree[0])
        r_orphan_nodes += new_tree[1]
        nrn_data = redef_idx(unfiltered_nrn_data)
        num_orphans += 1 
        file(nrn_data, output_path, num_orphans, orphan_file)  # Write separated neurons to files
        print(r_orphan_nodes, 'nodes connected to an orphan node.\n')
    if (returned_nodes + len(soma_indices[1]) == len(swc_data)) or (r_orphan_nodes + len(soma_indices[1]) == len(swc_data)): 
        print('All soma originating nodes plus orphan nodes separated.\n')
    else: 
        print('Not all nodes were separated. \n Please check the SWC data for errors, or orphan node connections.')
        
def soma_id_and_orphan(data): # Seems to work fine
    """
    Find soma indices in the SWC data.
    :param data: SWC data as a pandas DataFrame.
    :return: List of soma indices.
    """
    structure_identifier = 1 # column # in swc format for structure identifier
    parent_sample = 6 # column # in swc format for parent node
    # sample_num = 0 # column # in swc format for sample number
    soma = []
    orphans = []
    for index in range(len(data)):
        if data[index][structure_identifier] == 1 and data[index][structure_identifier] == 1:  # Check if the node is a soma
            soma.append(index)  # Append the soma node to the list of starting points
        elif data[index][parent_sample] == -1 and data[index][structure_identifier] != 1:
            orphans.append(index)
    return soma, orphans

def find_indices(arr, targets):
    """Finds all indices in an array that have the values listed in the targets array
    :param arr: An array of data to be searched through
    :param targets: An array of values to search for
    :return output: An array with the indices of every value that matches a value described in the target array"""
    target_set = set(targets)
    output = [i + 1 for i, v in enumerate(arr) if v in target_set]
    if len(output) == 0: 
        return(None)
    return output
# Example Usage
# print(find_indices(p, [12]))

def add_dict_entries(dictionary): 
    """Returns one array as a combination of many smaller arrays each with individual dictionary keys
    :param dictionary: The dictionary full of arrays to combine into one array
    :return output: One array consisting of all array values in the dictionary from every key"""
    output = []
    for i in range(len(dictionary) - 1): 
        output += dictionary[i + 1]
    return output

def soma_tree(dictionary, iteration, data, num_nodes): 
    """Separates individual neurons from network of neurons using swc data and dictionary keys. It finds all nodes connected to the previously located nodes. 
    :param dictionary: A dictionary with each key as an array of nodes connected to the nodes described in the previous key
    :param iteration: The number of iterations the recursive function has completed .
    :param data: The data of parent nodes in dictionary format to be updated each iteration.
    :param num_nodes: The total number of nodes that have been filtered through and isolated into an individual neuron. 
    :return output_arr: A single array of all indices in the swc_data that compose a single neuron.
    :return num_nodes: The total number of nodes that were isolated after isolating one individual neuron."""
    if dictionary.get(iteration) == None: # Checks and returns all indices of raw swc data of a specific soma starting point
        output_arr = add_dict_entries(dictionary)
        num_nodes += len(output_arr)
        return output_arr, num_nodes
    else: 
        parents = dictionary.get(iteration) # Recursive function that finds the indices of nodes that make up individual neurons with soma as starting points
        new_parents = find_indices(data['p'], parents)
        dictionary.update({(iteration + 1): new_parents})
        iteration += 1
        return soma_tree(dictionary, iteration, data, num_nodes)

def data_into_dictionary(data): 
    """Reorganizes raw data into a dictionary format for use in other functions.
    :param data: swc data as a pandas dataFrame.
    :return output_dictionary: dictionary with sample numbers and parent node information of swc data."""
    sample_num = 0 # define swc convention constants
    parent_sample = 6 
    indices_arr = [] # initialize arrays for use in function. 
    parents_arr = []
    for i in range(len(data)): 
        indices_arr.append(data[i][sample_num])
        parents_arr.append(data[i][parent_sample])
    output_dictionary = {'i': indices_arr, 'p': parents_arr}
    return(output_dictionary)
    
def data_idx_to_data(swc_data, idx_arr):
    """Gathers all raw swc data from pandas dataframe from array that holds index values of wanted data. 
    :param swc_data: Raw swc_data in pandas datafram format
    :param idx_array: An array of sample number indices of individual neuron cells.
    :return: Pandas Dataframe of swc raw data with only the indices of wanted data."""
    filtered_data = []
    # print(idx_arr)
    for index in idx_arr: 
        filtered_data.append(swc_data[index - 1])
    return filtered_data

def redef_idx(data): 
    """Redefine indices in the SWC data to match swc format convensions after node isolation.
    :param data: swc data as a pandas dataFrame.
    :return: DataFrame with redefined indices."""
    sample_num = 0 # Set constants for use
    parent_sample = 6
    new_sample_num = 0 # Initialize first sample number for swc format

    for idx in range(len(data)): 
        new_sample_num += 1
        for smpl in range(len(data)): 
            if data[idx][sample_num] == data[smpl][parent_sample]:
                data[smpl][parent_sample] = new_sample_num
        data[idx][sample_num] = new_sample_num
    return data  # Return the modified data           

def file(nrn_data, output_path, file_num, input_name): 
    """
    Write separated neurons to files.
    :param nrn: Separated neuron. 
    :param output_path: Path to save the output files.
    """
    import os
    if not os.path.exists(output_path): # Create export path
        os.makedirs(output_path)
    
    file_name = os.path.join(output_path, f'{input_name}_{file_num}.swc') # creates file name
    # f'
    with open(file_name, 'w') as f: # exports new file to export path
        for node in nrn_data:
            f.write(' '.join(map(str, node)) + '\n')

if __name__ == '__main__':
    # input_file = 'test_retinal_cells.swc'  # replace with your SWC file path
    # output_path = 'C:\\Users\\emanu\\USC-Summer\\nrn_sep_files'  # replace with your desired output directory
    main(input_file, output_path)





