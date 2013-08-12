import os, sys
from glob import glob
import nibabel as nib
import itertools

def make_dir(root, name = 'temp'):
    """ generate dirname string
    check if directory exists
    return exists, dir_string
    """
    outdir = os.path.join(root, name)
    exists = False
    if os.path.isdir(outdir):
        exists = True
    else:
        os.mkdir(outdir)
    return exists, outdir


def split_filename(fname):
    """split a filename into component parts

    Parameters
    ----------
    fname : str
        file or path name

    Returns
    -------
    pth : str
        base path of fname
    name : str
        name from fname without extension
    ext : str
        file extension from fname

    Examples
    --------
    >>> from filefun import split_filename
    >>> pth, name, ext = split_filename('/home/jagust/cindeem/test.nii.gz')
    >>> pth
    '/home/jagust/cindeem'

    >>> name
    'test'

    >>> ext
    'nii.gz'

    """
    pth, name = os.path.split(fname)
    tmp = '.none'
    ext = []
    while tmp:
        name, tmp = os.path.splitext(name)
        ext.append(tmp)
    ext.reverse()
    return pth, name, ''.join(ext)

    
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
    



def square_from_combos(array1D, nnodes):
    square_mat = np.zeros((nnodes,nnodes))
    indices = list(itertools.combinations(range(nnodes), 2))
    for i in range(len(array1D)):
        square_mat[indices[i]] = array1D[i]
    return square_mat + square_mat.T
