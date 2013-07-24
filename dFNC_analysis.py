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
dfnc_measures = ['FNCdyn', 'spectra_fnc']
dfnc_stats = {'mean':np.mean, 'std':np.std}
###############################

#Get analysis info  numbers
info_file = os.path.join(datadir, dfnc_info)
comp_nums, ncomps, nsubs = gift.dfnc_analysis_info(info_file)
features = (ncomps*(ncomps-1))/2

# Get list of subject mat files
sub_matfiles = glob(os.path.join(datadir, globstr))

for measure in dfnc_measures:
    for stat_name in dfnc_stats.keys():
        stat_func = dfnc_stats[stat_name]
        allsub_array = np.zeros((nsubs, features))
        for i in range(len(sub_matfiles)):
            subfile = sub_matfiles[i]
            sub_data = gift.get_dfnc_data(subfile, measure, stat_func)
            allsub_array[i] = sub_data
            outname = '_'.join(['dFNC', measure, stat_name]) + '.csv'
            outfile = os.path.join(datadir, outname)
            np.savetxt(outfile, allsub_array, delimiter='\t')
            
