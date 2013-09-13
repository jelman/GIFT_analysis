import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np

    
####################### Set parameters################
datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/dFNC'
dfnc_info = 'rsfmri_dfnc.mat'
globstr = '*_results.mat'
nnodes = 23
dfnc_measures = {'corr':'FNCdyn', 'spectra':'spectra_fnc'}
dfnc_stats = {'mean':np.mean, 'median':np.median, 'std':np.std}
modeldir = '/home/jagust/rsfmri_ica/GIFT/models/Old'
des_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.mat')
con_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.con')
subset = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
        20, 21, 22, 23, 24, 25, 26, 27, 28, 35, 39, 40, 41, 42, 43, 44, 45, 46, 
        47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 
        67, 68, 69, 70, 72, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 
        89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
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
        subset_array = allsub_array[subset,:]
        outname = '_'.join(['dFNC', measure_name, stat_name, group_name]) + '.csv'
        outfile = os.path.join(datadir, outname)
        np.savetxt(outfile, subset_array, fmt='%1.5f', delimiter='\t')
        
        

## Run group analysis with randomise
####################################
exists, resultsdir = gu.make_dir(datadir,'randomise') 
resultsglob = os.path.join(datadir, ''.join(['dFNC_','*',group_name,'.csv']))
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
