import scipy.io
import numpy as np

def dfnc_analysis_info(infile):
    mat = scipy.io.loadmat(infile)
    comp_nums = mat['dfncInfo']['comps'][0][0][0]
    ncomps = len(comp_nums)
    nsubs = len(mat['dfncInfo']['outputFiles'][0][0][0])
    return comp_nums, ncomps, nsubs
    

def get_dfnc_data(infile, measure, stat):
    mat = scipy.io.loadmat(infile)
    measure_mat = mat[measure]
    measure_stat = stat(measure_mat, axis=0)
    return measaure_stat
    
        
def fnctb_stats(infile):
    mat = scipy.io.loadmat(infile)
    fnc_corr = mat['adCorrAbs'][:,:,0]
    fnc_lag = mat['adCorrAbs'][:,:,1]
    return fnc_corr, fnc_lag
    
def square_from_combos(array1D, nnodes):
    square_mat = np.zeros((nnodes,nnodes))
    indices = list(itertools.combinations(range(nnodes), 2))
    for i in range(len(array1D)):
        square_mat[indices[i]] = array1D[i]
    return square_mat + square_mat.T

