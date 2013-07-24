import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as gift
from glob import glob
import numpy as np

    
#### Set parameters############
datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d40/dFNC'
dfnc_info = 'rsfmri_dfnc.mat'
globstr = '*_results.mat'
dyn_mean_out = 'dFNC_dyn_mean.csv'
dyn_std_out = 'dFNC_dyn_std.csv'
spectra_mean_out = 'dFNC_spectra_mean.csv'
spectra_std_out = 'dFNC_spectra_std.csv'
###############################

#Get analysis info  numbers
info_file = os.path.join(datadir, dfnc_info)
comp_nums, ncomps, nsubs = gift.dfnc_analysis_info(info_file)
features = (ncomps*(ncomps-1))/2

# Get list of subject mat files
sub_matfiles = glob(os.path.join(datadir, globstr))

# Create empty arrays
allsub_dyn_mean = np.zeros((nsubs, features))
allsub_spectra_mean = np.zeros((nsubs, features))
allsub_dyn_std = np.zeros((nsubs, features))
allsub_spectra_std = np.zeros((nsubs, features))

for i in range(len(sub_matfiles)):
    subfile = sub_matfiles[i]
    sub_dyn_mean, sub_dyn_std = gift.dfnc_dyn_stats(subfile)
    sub_spectra_mean, sub_spectra_std = gift.dfnc_spectra_stats(subfile)
    allsub_dyn_mean[i]=sub_dyn_mean   
    allsub_spectra_mean[i]=sub_spectra_mean
    allsub_dyn_std[i]=sub_dyn_std   
    allsub_spectra_std[i]=sub_spectra_std
    
dyn_mean_outfile = os.path.join(datadir, dyn_mean_out)
np.savetxt(dyn_mean_outfile, allsub_dyn_mean, delimiter='\t')
dyn_std_outfile = os.path.join(datadir, dyn_std_out)
np.savetxt(dyn_std_outfile, allsub_dyn_std, delimiter='\t')
spectra_mean_outfile = os.path.join(datadir, spectra_mean_out)
np.savetxt(spectra_mean_outfile, allsub_spectra_mean, delimiter='\t')
spectra_std_outfile = os.path.join(datadir, spectra_std_out)
np.savetxt(spectra_std_outfile, allsub_spectra_std, delimiter='\t')
