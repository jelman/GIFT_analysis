import os
import numpy as np
import scipy.io as sio
from glob import glob
import pandas as pd


def main(infiles, outname, nnodes, ntps, nsubs, tc_subset=False):
    assert len(infiles) == nsubs
    alltc = np.zeros((nsubs, ntps, nnodes))
    for i in range(nsubs):
        subfile = infiles[i]
        subtc_df = pd.read_csv(subfile, sep=',')
        if tc_subset:
            col_subset = [col for net in tc_subset for col in subtc_df.columns if net in col]
            subtc_df = subtc_df[col_subset]
        assert subtc_df.shape == (ntps, nnodes)
        alltc[i,:,:] = subtc_df
    outmat = {'tc' : alltc}
    sio.savemat(outname, outmat)
    print 'Timecourses saved to %s'%(outname)
            


            
if __name__ == '__main__':
    """
    Takes a list of timecourses saved as csv files and combines them in a mat file 
    of shape Nsubjects x Ntimepoints x Nnodes. This mat may be used as input to dFNC
    """

    ###################### Set parameters #############################
    datadir = '/home/jagust/rsfmri_ica/CPAC/connectivity/timecourses/Greicius_90_rois'
    outname = '/home/jagust/rsfmri_ica/CPAC/connectivity/dFNC/Greicius_90_rois.mat'
    dataglob = '*_timecourses.csv'
    nnodes = 54
    ntps = 185
    nsubs = 93
    tc_subset = ['anterior_Salience','dDMN','LECN','post_Salience','Precuneus','RECN','vDMN','Visuospatial']
    ####################################################################

    infiles = glob(os.path.join(datadir, dataglob))
    infiles.sort()
        
    main(infiles, outname, nnodes, ntps, nsubs, tc_subset)


