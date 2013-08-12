import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np

##### Set parameters ############
datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30/FNCtb'
fnctb_info = 'GraphAndData.mat'
nnodes = 11
fnc_corr_out = 'FNCtb_corr.csv'
fnc_corr_z_out = 'FNCtb_corr_z.csv'
fnc_lag_out = 'FNCtb_lag.csv'
modeldir = '/home/jagust/rsfmri_ica/GIFT/models'
des_file = os.path.join(modeldir, 'PIB_Age_Scanner_Motion_GM_log.mat')
con_file = os.path.join(modeldir, 'PIB_Age_Scanner_Motion_GM_log.con')
################################


## Get data from FNC toolbox output
#####################################
# Set output of FNC toolbox as infile
infile = os.path.join(datadir, fnctb_info)
# Get correlation and lag matrices
fnc_corr, fnc_corr_z, fnc_lag = go.get_fnctb_stats(infile)
# Save out text files of correlation and lags
fnc_corr_outfile = os.path.join(datadir, fnc_corr_out)
np.savetxt(fnc_corr_outfile, fnc_corr, fmt='%1.5f', delimiter='\t')
fnc_corr_z_outfile = os.path.join(datadir, fnc_corr_z_out)
np.savetxt(fnc_corr_z_outfile, fnc_corr_z, fmt='%1.5f', delimiter='\t')
fnc_lag_outfile = os.path.join(datadir, fnc_lag_out)
np.savetxt(fnc_lag_outfile, fnc_lag, fmt='%1.2f', delimiter='\t')

## Run group analysis
#######################
exists, resultsdir = gu.make_dir(datadir,'randomise') 
resultsglob = os.path.join(datadir, 'FNCtb_*.csv')
result_files = glob(resultsglob)
for fnc_data_file in result_files:
    fnc_data = np.genfromtxt(fnc_data_file, names=None, dtype=float, delimiter=None)
    pth, fname, ext = gu.split_filename(fnc_data_file)
    fnc_img_fname = os.path.join(resultsdir, fname + '.nii.gz')
    fnc_saveimg = gu.save_img(fnc_data, fnc_img_fname)
    rand_basename = os.path.join(resultsdir, fname)
    p_uncorr_list, p_corr_list = ga.randomise(fnc_saveimg, 
                                                rand_basename, 
                                                des_file, 
                                                con_file)     
    uncorr_results = ga.get_results(p_uncorr_list)
    corr_results = ga.get_results(p_corr_list)
           
    fdr_results = {}
    for i in range(len(uncorr_results.keys())):
        conname = sorted(uncorr_results.keys())[i]
        fdr_corr_arr = ga.multi_correct(uncorr_results[conname])
        fdr_results[conname] = gu.square_from_combos(fdr_corr_arr, nnodes)
        
        outfile = os.path.join(resultsdir, 
                            ''.join([rand_basename, '_fdr_corrp_','tstat',str(i+1),'.txt']))
        # Save results to file
        np.savetxt(outfile, 
                    fdr_results[conname], 
                    fmt='%1.5f', 
                    delimiter='\t')  
        print('Saved corrected output to %s'%(outfile))  
