import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np

    
####################### Set parameters################
datadir = '/home/jagust/rsfmri_ica/CPAC/connectivity/dFNC/L1_win22'
dfnc_info = 'greicius_rois.mat'
globstr = '*_results.mat'
nnodes = 54
dfnc_measures = {'corr':'FNCdyn', 'spectra':'spectra_fnc'}
dfnc_stats = {'mean':np.mean, 'median':np.median, 'std':np.std}
modeldir = '/home/jagust/rsfmri_ica/GIFT/models/Old'
des_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.mat')
con_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.con')
subset=False
group_name = 'Old'
##############################################################

#Get analysis info numbers
info_file = os.path.join(datadir, dfnc_info)
comp_nums, ncomps, nsubs, freq = go.dfnc_analysis_info(info_file)
features = (ncomps*(ncomps-1))/2

# Get list of subject mat files
sub_matfiles = glob(os.path.join(datadir, globstr))

## Get data from dFNC output
############################
for measure_name in dfnc_measures.keys():
    measure_field = dfnc_measures[measure_name]
    for stat_name in dfnc_stats.keys():
        stat_func = dfnc_stats[stat_name]
        allsub_array = np.zeros((nsubs, features))
        for i in range(len(sub_matfiles)):
        ### CUT OFF SPECTRAL ANALYSIS AT <0.25HZ ###
            subfile = sub_matfiles[i]
            sub_data = go.get_dfnc_data(subfile, measure_field)
            if measure_name == 'spectra':
                sub_data = sub_data[freq<0.025,:]
            sub_stat = go.get_dfnc_stat(sub_data, stat_func)
            allsub_array[i] = sub_stat
        # Save all subjects
        outname = '_'.join(['dFNC', measure_name, stat_name]) + '.csv'
        outfile = os.path.join(datadir, outname)
        np.savetxt(outfile, allsub_array, fmt='%1.5f', delimiter='\t')
        # Save only subset of subjects
        if subset:
            subset_array = allsub_array[subset,:]
            outname = '_'.join(['dFNC', measure_name, stat_name, group_name]) + '.csv'
            outfile = os.path.join(datadir, outname)
            np.savetxt(outfile, subset_array, fmt='%1.5f', delimiter='\t')
        
        

## Run group analysis with randomise
####################################
exists, resultsdir = gu.make_dir(datadir,'randomise') 
if subset:
    resultsglob = os.path.join(datadir, ''.join(['dFNC_','*',group_name,'.csv']))
else:
    resultsglob = os.path.join(datadir, ''.join(['dFNC_','*','.csv']))
result_files = glob(resultsglob)
for dfnc_data_file in result_files:
    dfnc_data = np.genfromtxt(dfnc_data_file, names=None, dtype=float, delimiter=None)
    pth, fname, ext = gu.split_filename(dfnc_data_file)
    dfnc_img_fname = os.path.join(resultsdir, fname + '.nii.gz')
    dfnc_saveimg = gu.save_img(dfnc_data, dfnc_img_fname)
    rand_basename = os.path.join(resultsdir, fname)
    p_uncorr_list, p_corr_list = ga.randomise(dfnc_saveimg, 
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
