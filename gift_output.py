import scipy.io
import numpy as np
from nipype.interfaces.base import CommandLine
import nibabel as nib
import statsmodels.stats.multitest as smm
import nipype.interfaces.fsl as fsl
import itertools

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
    return measure_stat
    

def fnctb_stats(infile):
    mat = scipy.io.loadmat(infile)
    fnc_corr = mat['adCorrAbs'][:,:,0]
    fnc_lag = mat['adCorrAbs'][:,:,1]
    return fnc_corr, fnc_lag


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


def randomise(infile, outname, design_file, contrast_file):   
    """
    Runs fsl randomise and returns list of outputs
    
    Parameters:
    ----------
    infile : str
        4d nifti file containing subject data concatenated over time
    outname : str
        base name for output
    design_file : str
        fsl group design file (.mat)
    contrast_file : str
        fsl contrast file (.con)
        
    Returns:
    ---------
    p_uncorrected : list
        paths to randomise outputs (nifti) containing uncorrected 1 - p values.
        one file per contrast (ex. *vox_p_tstat1.nii.gz)
    p_corrected : list
        list of randomise outputs (nifti) containing corrected 1 - p values      
        one file per contrast  (ex. *vox_corrp_tstat1.nii.gz)
    """
         
    cmd = ' '.join(['randomise -i %s'%(infile),
                    '-o %s'%(outname),
                    '-d %s'%(design_file),
                    '-t %s'%(contrast_file),
                    '-x -n 5000'])
    cout = CommandLine(cmd).run()
    if not cout.runtime.returncode == 0:
        print cout.runtime.stderr
        return None
    else:
        globstr = ''.join([outname, '_vox_p_tstat*.nii.gz'])
        p_uncorrected = glob(globstr)
        globstr = ''.join([outname, '_vox_corrp_tstat*.nii.gz'])
        p_corrected = glob(globstr)
        return p_uncorrected, p_corrected

def load_rand_img(infile):
    img = nib.load(infile)
    dat = img.get_data()
    return dat
    
def get_results(randomise_outputs):  
    """
    Takes a list of randomise image outputs and loads them into a 
    dictionary containing numpy array for further processing
    
    Parameters:
    -----------
    randomise_outputs : list
        list of files output by randomise (ex. *vox_p_tstat1.nii.gz)
    
    Returns:
    --------
    results : dict
        key = contrast name (ex. 'contrast1')
        value = numpy array containing 1 - p values 
                of group comparison output by randomise
    
    """
    
    results = {}  
    for i in range(len(randomise_outputs)):
        pth, fname, ext = split_filename(randomise_outputs[i])
        data_1minuspval = load_rand_img(randomise_outputs[i])
        data_pval = 1 - data_1minuspval
        outfile = os.path.join(pth, fname + '.txt')
        np.savetxt(outfile, 
                    data_pval, 
                    fmt='%1.3f', 
                    delimiter='\t')  
        print('p value matrix saved to %s'%(outfile))
        conname = ''.join(['contrast', str(i+1)])
        results[conname] = data_pval
    return results
            
def square_from_combos(array1D, nnodes):
    square_mat = np.zeros((nnodes,nnodes))
    indices = list(itertools.combinations(range(nnodes), 2))
    for i in range(len(array1D)):
        square_mat[indices[i]] = array1D[i]
    return square_mat + square_mat.T

