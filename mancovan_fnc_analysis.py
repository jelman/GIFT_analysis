import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np


if __name__ == '__main__':



    ##### Set parameters ############
    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/Mancovan/fnc_stats'
    mfnc_info = 'rsfmri_mancovan_results_fnc.mat'
    nnodes = 23
    mfnc_zcorr_out = 'mfnc_zcorr'
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
    infile = os.path.join(datadir, mfnc_info)
    # Get correlation and lag matrices
    mfnc_zcorr = go.get_mfnc_stats(infile)
    # Save out text files of correlation and lags
    mfnc_zcorr_outfile = os.path.join(datadir, ''.join([mfnc_zcorr_out,'.csv']))
    np.savetxt(mfnc_zcorr_outfile, mfnc_zcorr, fmt='%1.5f', delimiter=',')
    # Save out only subset group
    if subset:
        mfnc_zcorr_outfile = os.path.join(datadir, ''.join([mfnc_zcorr_out,'_',group_name,'.csv']))
        np.savetxt(mfnc_zcorr_outfile, mfnc_zcorr[subset,:], fmt='%1.5f', delimiter=',')

    ## Run group analysis
    #######################
    exists, resultsdir = gu.make_dir(datadir,'randomise') 
    if subset:
        resultsglob = os.path.join(datadir, ''.join(['mfnc_zcorr_','*',group_name,'.csv']))
    else:
        resultsglob = os.path.join(datadir, ''.join(['mfnc_zcorr_','*','.csv']))
    result_files = glob(resultsglob)
    for mfnc_data_file in result_files:
        mfnc_data = np.genfromtxt(mfnc_data_file, names=None, dtype=float, delimiter=None)
        pth, fname, ext = gu.split_filename(mfnc_data_file)
        mfnc_img_fname = os.path.join(resultsdir, fname + '.nii.gz')
        mfnc_saveimg = gu.save_img(mfnc_data, mfnc_img_fname)
        rand_basename = os.path.join(resultsdir, fname)
        p_uncorr_list, p_corr_list = ga.randomise(mfnc_saveimg, 
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
