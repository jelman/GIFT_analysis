import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import nibabel as nib
import numpy as np
import scipy.io as sio
import gift_utils as gu

def main(data_files):
    """
    Create matfile of subject matrices to be fed into NBS.
    
    Takes list of files containing n rows of subject with 1D vector of correlation or other matrices.
    These should only be upper or lower triangles of matrix. Saves out i,j,k mat file in which i and j
    are equal to number of nodes and k is the number of subjects.
    """
    
    for infile in data_files:
        dat = np.loadtxt(infile, delimiter=None)
        result_arr = np.zeros((nnodes, nnodes, dat.shape[0]))
        result_dict = {}
        for sub in range(dat.shape[0]):
            subdat = dat[sub, :]
            result_arr[:,:,sub] = gu.square_from_combos(subdat, nnodes) 
        result_dict['submats'] = result_arr
        pth, basename, ext = gu.split_filename(infile)
        outfile= os.path.join(outputdir, basename + '.mat')       
        sio.savemat(outfile, result_dict)    


if __name__ == '__main__':

    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/dFNC'
    outputdir = os.path.join(datadir, 'NBS')
    globstr = 'dFNC*_Old.csv'
    nnodes = 23
    data_files = glob(os.path.join(datadir, globstr))
    
    main(data_files)
    

