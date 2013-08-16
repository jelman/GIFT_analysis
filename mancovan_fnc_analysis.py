import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
sys.path.insert(0, '/home/jagust/jelman/CODE/misc')
import general_utilities as utils
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np
import itertools
import pandas as pd
import statsmodels.stats.multitest as smm

"""
Takes output of mancovan FNC analysis from GIFT toolbox and runs group stats (both OLS 
and robust linear model) using a specified design matrix. Writes file containing 
raw p-values, corrected p-valuesand t-scores of each pairwise comparison. 
"""

if __name__ == '__main__':


    ##### Set parameters ############
    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_Old_d30/Mancovan/fnc_stats'
    mfnc_info = 'rsfmri_mancovan_results_fnc.mat'
    mfnc_zcorr_out = 'mfnc_zcorr.csv'
    cov_file = '/home/jagust/rsfmri_ica/Spreadsheets/Covariates/Subject_Covariate_Old_log.csv'
    ################################


    ## Get data from FNC toolbox output
    #####################################
    # Set output of FNC toolbox as infile
    infile = os.path.join(datadir, mfnc_info)
    # Get selected component numbers and correlation and matrix
    comp_nums, mfnc_zcorr = go.get_mfnc_stats(infile)
    combos = gu.get_combo_names(comp_nums)
    # Save out text files of correlation and lags
    mfnc_zcorr_outfile = os.path.join(datadir, mfnc_zcorr_out)
    np.savetxt(mfnc_zcorr_outfile, mfnc_zcorr, fmt='%1.5f', delimiter='\t')



    ## Run group analysis with statsmodels modules
    ##############################################
    # Make results directory
    resultsdir = utils.make_dir(datadir,'results') 
    # Create empty dataframe to hold results of group analysis
    results_frame = pd.DataFrame(data=None, 
                                index=combos, 
                                columns=['OLS_pval','OLS_corrp','OLS_tscore',
                                        'RLM_pval','RLM_corrp','RLM_tscore'])
    # Load design file and prepend a constant
    X = ga.load_design(cov_file)
    # Find results of all mfnc analyses and loop over each 
    resultsglob = os.path.join(datadir, mfnc_zcorr_out)
    mfnc_data_file = glob(resultsglob)[0]


    mfnc_data = pd.read_csv(mfnc_data_file, delimiter='\t', names=combos)
    # Loop over each combination of ICs and run group analysis using specified model
    for comparison in mfnc_data.columns:
        y = mfnc_data[comparison] # select pairwise comparison as dependent var
        # Run OLS and append results
        ols_results = ga.run_ols(y, X)
        results_frame.ix[comparison]['OLS_pval'] = ols_results.pvalues['PIB_Index']
        results_frame.ix[comparison]['OLS_tscore'] = ols_results.tvalues['PIB_Index']
        # Run robust stats and append results
        rlm_results = ga.run_rlm(y, X)
        results_frame.ix[comparison]['RLM_pval'] = rlm_results.pvalues['PIB_Index']
        results_frame.ix[comparison]['RLM_tscore'] = rlm_results.tvalues['PIB_Index']
        
    # Get corrected p values
    _,results_frame['OLS_corrp'],_,_ = smm.multipletests(results_frame.OLS_pval,
                                                                        method='fdr_bh')
    _,results_frame['RLM_corrp'],_,_ = smm.multipletests(results_frame.RLM_pval,
                                                                        method='fdr_bh')

    # Save results to file
    pth, fname, ext = utils.split_filename(mfnc_data_file)
    new_fname = '_'.join([fname, 'results'])
    outfile = os.path.join(resultsdir, new_fname + ext)
    results_frame.to_csv(outfile, sep='\t', header=True, index=True)
    print('Saved corrected output to %s'%(outfile)) 
