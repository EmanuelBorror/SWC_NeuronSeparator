# SWC_NeuronSeparator
Expands the use of SWC files by taking swc data sets of neuron networks and isolates individual neurons and orphan nodes for further use or rendering.

This repository uses the SWCToolkit library. Ensure that this library is in the same folder as your script. 
https://github.com/jmbouteiller/SWCToolkit

# How to Use: 
To separate a network into its orphan nodes and individual neurons import nrn_sep into your script. Then use the function main() to separate individual neuron cells and orphan nodes. The new outputed swc_files will be located on the output path designated in the paramter of this function. 
