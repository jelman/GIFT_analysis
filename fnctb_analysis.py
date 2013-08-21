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
Takes output of FNCtb analysis from GIFT toolbox and runs group stats (both OLS 
and robust linear model) using a specified design matrix. Writes file containing 
raw p-values, corrected p-valuesand t-scores of each pairwise comparison. 
"""

if __name__ == '__main__':



    ##### Set parameters ############
    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75/FNCtb'
    fnctb_info = 'GraphAndData.mat'
    fnc_corr_out = 'FNCtb_corr.csv'
    fnc_corr_z_out = 'FNCtb_corr_z.csv'
    fnc_lag_out = 'FNCtb_lag.csv'
    cov_file = '/home/jagust/rsfmri_ica/Spreadsheets/Covariates/Subject_Covariate_Log_YoungOld_residGM_Age.csv'
    ################################


    ## Get data from FNC toolbox output
    #####################################
    # Set output of FNC toolbox as infile
    infile = os.path.join(datadir, fnctb_info)
    # Get selected components numbers, correlation and lag matrices
    comp_nums, fnc_corr, fnc_corr_z, fnc_lag = go.get_fnctb_stats(infile)
    combos = gu.get_combo_names(comp_nums)
    # Save out text files of correlation and lags
    fnc_corr_outfile = os.path.join(datadir, fnc_corr_out)
    np.savetxt(fnc_corr_outfile, fnc_corr, fmt='%1.5f', delimiter='\t')
    fnc_corr_z_outfile = os.path.join(datadir, fnc_corr_z_out)
    np.savetxt(fnc_corr_z_outfile, fnc_corr_z, fmt='%1.5f', delimiter='\t')
    fnc_lag_outfile = os.path.join(datadir, fnc_lag_out)
    np.savetxt(fnc_lag_outfile, fnc_lag, fmt='%1.2f', delimiter='\t')

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
    # Find results of all FNCtb analyses and loop over each 
    resultsglob = os.path.join(datadir, fnc_corr_z_out)
    fnctb_data_file = glob(resultsglob)[0]


    fnctb_data = pd.read_csv(fnctb_data_file, delimiter='\t', names=combos)
    # Loop over each combination of ICs and run group analysis using specified model
    for comparison in fnctb_data.columns:
        y = fnctb_data[comparison] # select pairwise comparison as dependent var
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
    pth, fname, ext = utils.split_filename(fnctb_data_file)
    new_fname = '_'.join([fname, 'results'])
    outfile = os.path.join(resultsdir, new_fname + ext)
    results_frame.to_csv(outfile, sep='\t', header=True, index=True)
    print('Saved corrected output to %s'%(outfile))        

