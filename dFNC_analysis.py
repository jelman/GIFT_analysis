import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as go
import gift_analysis as ga
import gift_utils as gu
from glob import glob
import numpy as np
import itertools
import pandas as pd
import statsmodels.stats.multitest as smm

"""
Takes output of dFNC analysis from GIFT toolbox and runs group stats (both OLS 
and robust linear model) using a specified design matrix. Writes file containing 
raw p-values, corrected p-valuesand t-scores of each pairwise comparison. 
"""


if __name__ == '__main__':


  
    ####################### Set parameters################
    datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30/dFNC'
    dfnc_info = 'rsfmri_dfnc.mat'
    globstr = '*_results.mat'
    nnodes = 11
    dfnc_measures = {'corr':'FNCdyn', 'spectra':'spectra_fnc'}
    dfnc_stats = {'mean':np.mean, 'std':np.std}
    cov_file = '/home/jagust/rsfmri_ica/Spreadsheets/Covariates/Subject_Covariate_All_log.csv'
    ##############################################################

    #Get analysis info
    info_file = os.path.join(datadir, dfnc_info)
    comp_nums, ncomps, nsubs, freq = go.dfnc_analysis_info(info_file)
    features = (ncomps*(ncomps-1))/2
    combos = gu.get_combo_names(comp_nums)
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
                subfile = sub_matfiles[i]
                sub_data = go.get_dfnc_data(subfile, measure_field)
                if measure_name == 'spectra':
                    sub_data = sub_data[freq<0.025,:] # Only analyse freqs <0.025
                sub_stat = go.get_dfnc_stat(sub_data, stat_func)
                allsub_array[i] = sub_stat
            # Write out results of dFNC analysis
            outname = '_'.join(['dFNC', measure_name, stat_name]) + '.csv'
            outfile = os.path.join(datadir, outname)
            np.savetxt(outfile, allsub_array, fmt='%1.5f', delimiter='\t')
            

    ## Run group analysis with statsmodels modules
    ##############################################

    # Make results directory
    exists, resultsdir = gu.make_dir(datadir,'results') 
    # Create empty dataframe to hold results of group analysis
    results_frame = pd.DataFrame(data=None, 
                                index=combos, 
                                columns=['OLS_pval','OLS_corrp','OLS_tscore',
                                        'RLM_pval','RLM_corrp','RLM_tscore'])
    # Load design file and prepend a constant
    X = ga.load_design(cov_file)
    # Find results of all dfnc analyses and loop over each 
    resultsglob = os.path.join(datadir, 'dFNC_*.csv')
    result_files = glob(resultsglob)
    for dfnc_data_file in result_files:
        dfnc_data = pd.read_csv(dfnc_data_file, delimiter='\t', names=combos)
        # Loop over each combination of ICs and run group analysis using specified model
        for comparison in dfnc_data.columns:
            y = dfnc_data[comparison] # select pairwise comparison as dependent var
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
        pth, fname, ext = gu.split_filename(dfnc_data_file)
        new_fname = '_'.join([fname, 'results'])
        outfile = os.path.join(resultsdir, new_fname + ext)
        results_frame.to_csv(outfile, sep='\t', header=True, index=True)
        print('Saved corrected output to %s'%(outfile))        
