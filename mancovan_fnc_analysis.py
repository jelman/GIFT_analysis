import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as gift
from glob import glob
import numpy as np

##### Set parameters ############
datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/Mancovan/fnc_stats'
mfnc_info = 'rsfmri_mancovan_results_fnc.mat'
nnodes = 19
mfnc_zcorr_out = 'mfnc_zcorr.csv'
modeldir = '/home/jagust/rsfmri_ica/GIFT/models'
des_file = os.path.join(modeldir, 'PIB_Age_Scanner_Motion_GM_log.mat')
con_file = os.path.join(modeldir, 'PIB_Age_Scanner_Motion_GM_log.con')
################################


## Get data from FNC toolbox output
#####################################
# Set output of FNC toolbox as infile
infile = os.path.join(datadir, mfnc_info)
# Get correlation and lag matrices
mfnc_zcorr = gift.get_mfnc_stats(infile)
# Save out text files of correlation and lags
mfnc_zcorr_outfile = os.path.join(datadir, mfnc_zcorr_out)
np.savetxt(mfnc_zcorr_outfile, mfnc_zcorr, fmt='%1.5f', delimiter='\t')

## Run group analysis
#######################
exists, resultsdir = gift.make_dir(datadir,'randomise') 
resultsglob = os.path.join(datadir, 'mfnc_zcorr.csv')
result_files = glob(resultsglob)
for mfnc_data_file in result_files:
    mfnc_data = np.genfromtxt(mfnc_data_file, names=None, dtype=float, delimiter=None)
    pth, fname, ext = gift.split_filename(mfnc_data_file)
    mfnc_img_fname = os.path.join(resultsdir, fname + '.nii.gz')
    mfnc_saveimg = gift.save_img(mfnc_data, mfnc_img_fname)
    rand_basename = os.path.join(resultsdir, fname)
    p_uncorr_list, p_corr_list = gift.randomise(mfnc_saveimg, 
                                                rand_basename, 
                                                des_file, 
                                                con_file)     
    uncorr_results = gift.get_results(p_uncorr_list)
    corr_results = gift.get_results(p_corr_list)
           
    fdr_results = {}
    for i in range(len(uncorr_results.keys())):
        conname = sorted(uncorr_results.keys())[i]
        fdr_corr_arr = gift.multi_correct(uncorr_results[conname])
        fdr_results[conname] = gift.square_from_combos(fdr_corr_arr, nnodes)
        
        outfile = os.path.join(resultsdir, 
                            ''.join([rand_basename, '_fdr_corrp_','tstat',str(i+1),'.txt']))
        # Save results to file
        np.savetxt(outfile, 
                    fdr_results[conname], 
                    fmt='%1.5f', 
                    delimiter='\t')  
        print('Saved corrected output to %s'%(outfile))  
