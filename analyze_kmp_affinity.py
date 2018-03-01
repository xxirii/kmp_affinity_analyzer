"""
Simple script for how to use the lib_affinity library
"""

# ______________________________________________________________________________
# Useful libraries

import matplotlib.pyplot as plt
import numpy as np
import sys as sys
import matplotlib.gridspec as gridspec
import matplotlib as mpl
from lib_affinity import *


if __name__ == "__main__":

  argv = sys.argv[1:]
  if len(argv) > 0:
    input_file = argv[0]
  else:
    #Example:
    input_file = 'knl_flat_snc4_default'
    #input_file = 'knl_flat_snc4_g=core_scatter'
    #input_file = 'knl_flat_snc4_g=fine_scatter'
    #input_file = 'knl_flat_snc4_g=fine_compact'
    #input_file = 'knl_flat_snc4_g=fine_compact_2'
    #input_file = 'knl_flat_snc4_temp'
     
  # Create object
  affinity = Affinity()
  
  # Read from file
  affinity.read_file(input_file)    
  
  # Output report in a file
  affinity.output_in_file(input_file+'_report')
  
  # Show in terminal
  affinity.show()

  # Plot the results
  #fig = plt.figure(figsize=(12,7))
  #gs = gridspec.GridSpec(2, 2)
  #ax = plt.subplot(gs[:, :]) 

  #affinity.plot(fig,ax)

  #plt.show()
