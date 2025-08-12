# SWC_NeuronSeparator
Expands the use of SWC files by taking swc data sets of neuron networks and isolates individual neurons and orphan nodes for further use or rendering.

This repository uses the SWCToolkit library. Ensure that this library is in the same folder as your script. 
https://github.com/jmbouteiller/SWCToolkit

# How to Use: 
Firstly ensure nrn_sep.py is in the same folder as your script. To separate a network into its orphan nodes and individual neurons import nrn_sep into your script. Initialize the path to the swc file on your device as the first parameter to main(). The second parameter is the path to the desired location on your device. Then use the function main() to separate individual neuron cells and orphan nodes. The new outputed swc files will be located in the output path. Try following the example with the swc file provided ('test_retinal_cells.swc')
# Example: 
# To Run within another script: 
import nrn_sep as ns  
input_path  = 'path_to_swc'  
output_path = 'path_to_desired_location'  
ns.main(input_path, output_path)  
# To Run alone: 
At the bottom of the script uncomment "input_file" and "output_path" and replace those variables with the desired path. Then run the script. 
if __name__ == '__main__':
    # input_file = 'path_to_swc'  # replace with your SWC file path  
    # output_path = 'path_to_desired_location'  # replace with your desired output directory  
    main(input_file, output_path)  
