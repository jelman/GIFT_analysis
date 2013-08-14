import scipy.io
import os, sys
import numpy as np



def dfnc_analysis_info(infile):
    mat = scipy.io.loadmat(infile)
    comp_nums = mat['dfncInfo']['comps'][0][0][0]
    ncomps = len(comp_nums)
    nsubs = len(mat['dfncInfo']['outputFiles'][0][0][0])
    freq = mat['dfncInfo']['freq'][0][0][0]
    return comp_nums, ncomps, nsubs, freq
    

def get_dfnc_data(infile, measure):
    mat = scipy.io.loadmat(infile)
    measure_mat = mat[measure]
    return measure_mat

    
def get_dfnc_stat(data, stat_func):
    sub_stat = stat_func(data, axis=0)
    return sub_stat
    

def get_fnctb_stats(infile):
    mat = scipy.io.loadmat(infile)
    comp_nums = mat['gFnc']['anSelComp'][0][0]
    comp_nums = comp_nums.reshape((-1,))
    fnc_corr = mat['adCorrAbs'][:,:,0]
    fnc_corr_z = np.arctanh(fnc_corr)
    fnc_lag = mat['adCorrAbs'][:,:,1]
    return comp_nums, fnc_corr, fnc_corr_z, fnc_lag


def get_mfnc_stats(infile):
    mat = scipy.io.loadmat(infile) 
    comp_nums = mat['comp_number'][0]
    mfnc_zcorr = mat['fnc_corrs']
    return comp_nums, mfnc_zcorr
    




    
    

