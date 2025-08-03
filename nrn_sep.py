from swcToolkit import swcToolkit
import os 
import numpy as np
import sys

input_file = 'test_retinal_cells.swc' # replace with your SWC file path
output_path = 'C:\\Users\\emanu\\USC-Summer\\nrn_sep_files'  # replace with your desired output directory

# swc = swcToolkit() # load swc tool kit for use throughout
# swc_data = swc.read_swc_file(input_file)  # Read SWC data
# # swc_data = pd.read_csv(input_file, sep=r'\s+', comment='#', header=None) # Read SWC data using pandas
# print("Size:", np.shape(swc_data))
# print("Length:", np.size(swc_data))

def main(input_file, output_path): 
    """
    Main function to separate neurons based on SWC data.
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
    # Find soma indices in the SWC data
    # structure_identifier = 1 # column # in swc format for structure identifier
    # parent_sample = 6 # column # in swc format for parent node
    # sample_num = 0 # column # in swc format for sample number
    soma_indices = soma_id_and_orphan(swc_data)
    dictionary_data = data_into_dictionary(swc_data)
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
        file(nrn_data, output_path, num_orphans, orphan_file)  # Write se parated neurons to files
        print(r_orphan_nodes, 'nodes connected to an orphan node.\n')
    if returned_nodes + len(soma_indices[1]) == len(swc_data): 
        print('All soma originating nodes plus orphan nodes separated.\n')
        
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

# def sep_nrn(data, soma_index):
#     """
#     Separate neurons based on soma indices.
#     :param data: SWC data as a pandas DataFrame.
#     :param soma_indices: List of soma indices.
#     :return: List of separated neurons.
#     """
#     # structure_identifier = 1 # column # in swc format for structure identifier
#     parent_sample = 6 # column # in swc format for parent node
#     # sample_num = 0 # column # in swc format for sample number
#     nrn = []
#     parents = []
#     parents.append(soma_index) # Start with soma indices as parents
#     nrn.append(data[soma_index])  # Append the soma node to the neuron list
#     # print("Soma parent found:", parents)
#     while len(parents) > 0:
#         # print("Current parents:", parents)
#         for n in parents: 
#             new_parents = []
#             for index in range(len(data)): 
#                 if data[index][parent_sample] == n + 1: 
#                     nrn.append(data[index])
#                     new_parents.append(index)
#             parents = new_parents # This part overwrites the parents list with the new parents found 
# # write recursive function to find all children of a parent node
# # use with dictionary to store the children of each parent node
# # AI: pytorch (easy) TinserFlow (hard)
# # data arrays called tinsers
# # conceptualize numpy arrays as tensors

#     print("Length of neuron data after separation:", len(nrn))
#     return nrn           

def find_indices(arr, targets):
    target_set = set(targets)
    output = [i + 1 for i, v in enumerate(arr) if v in target_set]
    if len(output) == 0: 
        return(None)
    return output
# Example Usage
# print(find_indices(p, [12]))

def add_dict_entries(dictionary): 
    output = []
    for i in range(len(dictionary) - 1): 
        output += dictionary[i + 1]
    return output
# Example Usage 
# print(add_dict_entries(n))

def soma_tree(dictionary, iteration, data, num_nodes): 
    # print(iteration)
    if dictionary.get(iteration) == None: 
        output_arr = add_dict_entries(dictionary)
        num_nodes += len(output_arr)
        return output_arr, num_nodes
    else: 
        # print(dictionary)
        parents = dictionary.get(iteration)
        new_parents = find_indices(data['p'], parents)
        # print(new_parents)
        dictionary.update({(iteration + 1): new_parents})
        iteration += 1
        return soma_tree(dictionary, iteration, data, num_nodes)

def data_into_dictionary(data): 
    sample_num = 0 
    parent_sample = 6 
    indices_arr = []
    parents_arr = []
    for i in range(len(data)): 
        indices_arr.append(data[i][sample_num])
        parents_arr.append(data[i][parent_sample])
    output_dictionary = {'i': indices_arr, 'p': parents_arr}
    return(output_dictionary)
    
def data_idx_to_data(swc_data, idx_arr):
    filtered_data = []
    # print(idx_arr)
    for index in idx_arr: 
        filtered_data.append(swc_data[index - 1])
    return filtered_data

def redef_idx(data): 
    """Redefine indices in the SWC data.
    :param data: swc data as a pandas dataFrame.
    :return: DataFrame with redefined indices."""
    sample_num = 0
    parent_sample = 6
    new_sample_num = 0 

    for idx in range(len(data)): 
        new_sample_num += 1
        for smpl in range(len(data)): 
            if data[idx][sample_num] == data[smpl][parent_sample]:
                data[smpl][parent_sample] = new_sample_num
        data[idx][sample_num] = new_sample_num
    # print("Length of data after redefining indices:", len(data))
    return data  # Return the modified data           

def file(nrn_data, output_path, file_num, input_name): # Works Great
    """
    Write separated neurons to files.
    :param nrn: Separated neuron. 
    :param output_path: Path to save the output files.
    """
    import os
    # structure_identifier = 1 # column # in swc format for structure identifier
    # parent_sample = 6 # column # in swc format for parent node
    # sample_num = 0 # column # in swc format for sample number
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    file_name = os.path.join(output_path, f'{input_name}_{file_num}.swc')
    # f'
    with open(file_name, 'w') as f:
        for node in nrn_data:
            f.write(' '.join(map(str, node)) + '\n')

if __name__ == '__main__':
    input_file = 'test_retinal_cells.swc'  # replace with your SWC file path
    output_path = 'C:\\Users\\emanu\\USC-Summer\\nrn_sep_files'  # replace with your desired output directory
    main(input_file, output_path)

# Write another function that reads all the nodes that are stored in a new nrn function, and removes it from the swc_data file
# This way you can make the process quicker as you read less nodes each time, and you minimize repeated data

# somas = soma_id(swc_data)
# sep_nrn_data = sep_nrn(swc_data, somas[0])  # Example usage with the first soma index
# print(sep_nrn_data)


