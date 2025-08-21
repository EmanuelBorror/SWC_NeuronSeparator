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
    swc = swcToolkit() # load swc tool kit for use throughout
    swc_data = swc.read_swc_file(input_file)  # Read SWC data
    recursion_limit = len(swc_data) + 1 # changes the recursion limit so that recursive function can be called more than 5 times.
    sys.setrecursionlimit(recursion_limit)
    # Find soma indices in the SWC data
    # structure_identifier = 1 # column # in swc format for structure identifier
    # parent_sample = 6 # column # in swc format for parent node
    # sample_num = 0 # column # in swc format for sample number
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
        swc_data_index = soma_indices[0][idx]
        # print(swc_data_index, 'is the current soma index in the swc_data.\n')
        tree = {1: [swc_data[swc_data_index][sample_col]]}
        new_tree = soma_tree(tree, iteration, dictionary_data, num_nodes)
        unfiltered_nrn_data = data_idx_to_data(swc_data, new_tree[0])
        returned_nodes += new_tree[1]
        nrn_data = redef_idx(unfiltered_nrn_data)
        num_soma += 1 
        file(nrn_data, output_path, num_soma, file_name, soma_file = True)  # Write se parated neurons to files
        print(returned_nodes, 'nodes separated.\n')

    for idx in range(len(soma_indices[1])): 
        num_nodes = 0
        iteration = 1
        swc_data_index = soma_indices[1][idx]
        # print(swc_data_index, 'is the current orphan start node index in the swc_data.\n')
        tree = {1: [swc_data[swc_data_index][sample_col]]}
        new_tree = soma_tree(tree, iteration, dictionary_data, num_nodes)
        unfiltered_nrn_data = data_idx_to_data(swc_data, new_tree[0])
        r_orphan_nodes += new_tree[1]
        nrn_data = redef_idx(unfiltered_nrn_data)
        num_orphans += 1 
        file(nrn_data, output_path, num_orphans, file_name, soma_file = False)  # Write separated neurons to files
        print(r_orphan_nodes, 'nodes connected to an orphan node.\n')
    # Check if all nodes were separated
    if (returned_nodes + r_orphan_nodes == len(swc_data)): 
        print('All nodes separated successfully.\n')
        print('Total number of nodes in swc data:', len(swc_data))
        print('Total number of nodes separated:', returned_nodes + r_orphan_nodes)
        print('Total number of soma nodes: ', len(soma_indices[0]))
        print('Total number of orphan nodes: ', len(soma_indices[1]))
        print('Total number of nodes connected to soma:', returned_nodes)
        print('Total number of nodes connected to orphan nodes:', r_orphan_nodes)
    else: 
        print('Not all nodes were separated. \nPlease check the SWC data for errors, or orphan node connections.')
        print('Total number of nodes in swc data:', len(swc_data))
        print('Total number of nodes separated:', returned_nodes + r_orphan_nodes)
        print('Total number of soma nodes: ', len(soma_indices[0]))
        print('Total number of orphan nodes: ', len(soma_indices[1]))
        print('Total number of nodes connected to soma:', returned_nodes)
        print('Total number of nodes connected to orphan nodes:', r_orphan_nodes)
        
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
    from pprint import pprint
    import numpy as np
    new_sample_num = 0 # Initialize first sample number for swc format
    data = sort_by_id(data)
    # pprint(data)
    for i in range(len(data)): 
        new_sample_num += 1
        current_id = data[i]['id']
        # print("Checking Parents equal to:", current_id) 
        for j in range(len(data)): 
            current_parent = data[j]['parent']
            # print(current_parent)
            if (current_parent == current_id):
                data[j]['parent'] = new_sample_num
        data[i]['id'] = new_sample_num
    return data      

def sort_by_id(data): 
    """Sorts SWC data by ID value so it starts at the lowest and ends at the highest value to counter overwriting.
    :param data: swc data as a pandas dataFrame.
    :return: DataFrame sorted by ID."""
    id_list = [] 
    new_data = [] 
    for i in range(len(data)): 
        id_list.append(data[i]['id'])
    id_list.sort()
    # print(len(id_list))
    # print(id_list, '\n')
    for i in range(len(id_list)): 
        find_value = id_list[i]
        for j in range(len(data)):
            if data[j]['id'] == find_value:
                new_data.append(data[j])
                break
    return new_data

def file(nrn_data, output_path, file_num, input_name, soma_file): 
    """
    Write separated neurons to files.
    :param nrn: Separated neuron. 
    :param output_path: Path to save the output files.
    """
    import os
    if not os.path.exists(output_path): # Create export path
        os.makedirs(output_path)
    if soma_file == True: # If the file is a soma file, add soma to the file name
        file_name = os.path.join(output_path, f'{input_name}_{file_num}.swc') # creates file name
    elif soma_file == False: 
        file_name = os.path.join(output_path, f'{input_name}_orphan_{file_num}.swc') # creates file name for orphan nodes
    with open(file_name, 'w') as f: # exports new file to export path
        for node in nrn_data:
            f.write(' '.join(map(str, node)) + '\n')

if __name__ == '__main__':
    # input_file = 'swc_text_test.swc'  # replace with your SWC file path
    # output_path = 'C:\\Users\\emanu\\USC-Summer\\nrn_sep_files'  # replace with your desired output directory
    main(input_file, output_path)




