import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_utils
import numpy as np
from nipype.interfaces.base import CommandLine
import nibabel as nib
import statsmodels.stats.multitest as smm
import statsmodels.api as sm

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
                    '-D -x -n 5000'])
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
        pth, fname, ext = gift_utils.split_filename(randomise_outputs[i])
        data_1minuspval = load_rand_img(randomise_outputs[i])
        data_pval = 1 - data_1minuspval
        outfile = os.path.join(pth, fname + '.txt')
        np.savetxt(outfile, 
                    data_pval, 
                    fmt='%1.5f', 
                    delimiter='\t')  
        print('p value matrix saved to %s'%(outfile))
        conname = ''.join(['contrast', str(i+1)])
        results[conname] = data_pval
    return results


def multi_correct(data, meth='fdr_bh'):
    """
    Run fdr correction on nodes of interest contained in an array of p values. 
    
    Parameters:
    -----------
    data : numpy array
        nnodes x nnodes array containing p values of correlation between each node
    noi_idx : numpy
        indices (applicable to both row and column) of nodes of interest. This
        reduces the number of nodes corrected for
    meth : str
        Method of correction. Options are: 
            `bonferroni` : one-step correction
            `sidak` : on-step correction
            `holm-sidak` :
            `holm` :
            `simes-hochberg` :
            `hommel` :
            `fdr_bh` : Benjamini/Hochberg (default)
            `fdr_by` : Benjamini/Yekutieli 
    
    Returns:
    ----------
    fdr_corrected : numpy array
        array containing p values corrected with fdr
    """
    rej, corrp, alpha_sidak, alpha_bonnf = smm.multipletests(data, 
                                                            alpha=0.05, 
                                                            method=meth)
    return corrp
