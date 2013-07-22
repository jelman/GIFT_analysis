import scipy.io
import os
from glob import glob
import numpy as np

def analysis_info(infile):
    mat = scipy.io.loadmat(infile)
    comp_nums = mat['dfncInfo']['comps'][0][0][0]
    ncomps = len(comp_nums)
    nsubs = len(mat['dfncInfo']['outputFiles'][0][0][0])
    return comp_nums, ncomps, nsubs
    
def get_dyn_summary(infile):
    mat = scipy.io.loadmat(infile)
    fnc_dyn = mat['FNCdyn']
    dyn_mean = fnc_dyn.mean(axis=0)
    dyn_std = fnc_dyn.std(axis=0)
    return dyn_mean, dyn_std

def get_spectra_summary(infile):
    mat = scipy.io.loadmat(infile)
    spectra_fnc = mat['spectra_fnc']
    spectra_mean = spectra_fnc.mean(axis=0)
    spectra_std = spectra_fnc.std(axis=0)
    return spectra_mean, spectra_std
    
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
comp_nums, ncomps, nsubs = analysis_info(info_file)
features = (ncomps*(ncomps-1))/2

# Get list of subject mat files
sub_matfiles = glob(os.path.join(datadir, globstr))
# Create empty array
allsub_dyn_mean = np.zeros((nsubs, features))
allsub_spectra_mean = np.zeros((nsubs, features))
allsub_dyn_std = np.zeros((nsubs, features))
allsub_spectra_std = np.zeros((nsubs, features))

for i in range(len(sub_matfiles)):
    subfile = sub_matfiles[i]
    sub_dyn_mean, sub_dyn_std = get_dyn_summary(subfile)
    sub_spectra_mean, sub_spectra_std = get_spectra_summary(subfile)
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
