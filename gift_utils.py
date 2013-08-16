import os, sys
import itertools
import numpy as np


def add_squares(dat):
    return np.hstack((dat, dat**2))

def glm(X,Y):
    """ a simple GLM function returning the estimated parameters and residuals """
    betah   =  np.linalg.pinv(X).dot(Y)
    Yfitted =  X.dot(betah)
    resid   =  Y - Yfitted
    return betah, Yfitted, resid
    
    
def get_combo_names(comp_nums):
    combos = list(itertools.combinations(comp_nums, 2))
    combo_names = ['ic'+str(a)+'ic'+str(b) for a, b in combos]
    return combo_names


def square_from_combos(array1D, nnodes):
    square_mat = np.zeros((nnodes,nnodes))
    indices = list(itertools.combinations(range(nnodes), 2))
    for i in range(len(array1D)):
        square_mat[indices[i]] = array1D[i]
    return square_mat + square_mat.T
    
def save_img(data, fname):
    """
    Save netmat to 4d nifti image
    
    Parameters
    ----------
    data : array
        matrix of correlation metrics after r to z transform
        (nsub X nnodes*nnodes)
        
    fname : string
        name and path of output file to be saved
    """
    nnodes_sq = data.shape[1]
    nsubs = data.shape[0]
    dataT = data.T
    data4D = dataT.reshape(nnodes_sq, 1, 1, nsubs)
    img = nib.Nifti1Image(data4D, np.eye(4))
    img.to_filename(fname)
    return fname
