import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np


if __name__ == '__main__':


    ##### Set parameters ############
    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/FNCtb'
    fnctb_info = 'GraphAndData.mat'
    nnodes = 23
    fnc_corr_out = 'FNCtb_corr'
    fnc_corr_z_out = 'FNCtb_corr_z'
    fnc_lag_out = 'FNCtb_lag'
    modeldir = '/home/jagust/rsfmri_ica/GIFT/models/Old'
    des_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.mat')
    con_file = os.path.join(modeldir, 'Covariate_Old_log_demeaned.con')
    subset = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
            20, 21, 22, 23, 24, 25, 26, 27, 28, 35, 39, 40, 41, 42, 43, 44, 45, 46, 
            47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 
            67, 68, 69, 70, 72, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 
            89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
    group_name = 'Old'
    ################################


    ## Get data from FNC toolbox output
    #####################################
    # Set output of FNC toolbox as infile
    infile = os.path.join(datadir, fnctb_info)
    # Get correlation and lag matrices
    fnc_corr, fnc_corr_z, fnc_lag = go.get_fnctb_stats(infile)
    # Save out text files of correlation and lags
    fnc_corr_outfile = os.path.join(datadir, ''.join([fnc_corr_out,'.csv']))
    np.savetxt(fnc_corr_outfile, fnc_corr, fmt='%1.5f', delimiter=',')
    fnc_corr_z_outfile = os.path.join(datadir, ''.join([fnc_corr_z_out,'.csv']))
    np.savetxt(fnc_corr_z_outfile, fnc_corr_z, fmt='%1.5f', delimiter=',')
    fnc_lag_outfile = os.path.join(datadir, ''.join([fnc_lag_out,'.csv']))
    np.savetxt(fnc_lag_outfile, fnc_lag, fmt='%1.2f', delimiter=',')
    # Save out only subset group
    if subset:
        fnc_corr_outfile = os.path.join(datadir, ''.join([fnc_corr_out,'_',group_name,'.csv']))
        np.savetxt(fnc_corr_outfile, fnc_corr[subset,:], fmt='%1.5f', delimiter=',')
        fnc_corr_z_outfile = os.path.join(datadir, ''.join([fnc_corr_z_out,'_',group_name,'.csv']))
        np.savetxt(fnc_corr_z_outfile, fnc_corr_z[subset,:], fmt='%1.5f', delimiter=',')
        fnc_lag_outfile = os.path.join(datadir, ''.join([fnc_lag_out,'_',group_name,'.csv']))
        np.savetxt(fnc_lag_outfile, fnc_lag[subset,:], fmt='%1.2f', delimiter=',')

    ## Run group analysis
    #######################
    exists, resultsdir = gu.make_dir(datadir,'randomise') 
    if subset:
        resultsglob = os.path.join(datadir, ''.join(['FNCtb_','*',group_name,'.csv']))
    else:
        resultsglob = os.path.join(datadir, ''.join(['FNCtb_','*','.csv']))
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
                        delimiter=',')  
            print('Saved corrected output to %s'%(outfile))  
