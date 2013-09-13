import os, sys
import shutil
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
sys.path.insert(0, '/home/jagust/jelman/CODE/misc')
import general_utilities as utils
import gift_utils as gu
from glob import glob
import numpy as np


def backup_data(datadir, filelist):
    """
    back up all files in datadir matching pattern specified by globstr
    """
    backupdir = utils.make_dir(icadir, 'backups')
    for src in filelist:
        try:
            shutil.copy(src,backupdir)
        except:
            raise IOError('%s not copied'%src)
            
def find_sub_file(subnum, filelist):
    """
    returns file of a specified subject contained in a list of files
    """    
    subfile = [x for x in filelist if subnum in x]
    return subfile[0]    

def load_mcpars(datadir, subid):
    """
    load 6 column motion correction parameter file into numpy array
    """    
    subdir = os.path.join(datadir, '_'.join([subid, 'Preproc.feat']))
    mcpar_file = os.path.join(subdir, 'mc', 'prefiltered_func_data_mcf.par')
    mcpars = np.loadtxt(mcpar_file)
    return mcpars

def clean_timecourse(tc_file, mcpars):
    tc_dat, tc_aff = utils.load_nii(tc_file)
    betah, Yfitted, resid = gu.glm(mcpars, tc_dat)
    tc_cleaned = utils.save_nii(tc_file, resid, tc_aff)
    return tc_cleaned

def main(icadir, datadir, tc_fname, cmat_fname):
    tc_files = glob(os.path.join(icadir,tc_fname%('*')))
    cmat_files = glob(os.path.join(icadir,cmat_fname%('*')))
    backup_data(datadir, tc_files)
    backup_data(datadir, cmat_files)
    subid_map = utils.load_mapping(os.path.join(icadir, 'subid_mapping.txt'))
    for subid in sorted(subid_map.keys()):
        num = subid_map[subid]
        subnum = ''.join(['sub','%03d'%num])
        sub_mcpars = load_mcpars(datadir, subid)
        sub_mcpars_full = gu.add_squares(sub_mcpars)
        subtc_file = os.path.join(icadir, tc_fname%(subnum))
        subtc_clean = clean_timecourse(subtc_file, sub_mcpars_full)

        
if __name__ == '__main__':
    
    ##### Set parameters ##########
    icadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d75' # Directory containing ica output
    datadir = '/home/jagust/rsfmri_ica/GIFT/data' # Directory containing pre-processed data
    tc_fname = 'rsfmri_%s_timecourses_ica_s1_.nii' # File name pattern to search for tc files
    cmat_fname = 'rsfmri_ica_c%s-1.mat'
    ################################
    
    # Regress motion parameters out of component timecourses
    main(icadir, datadir, tc_fname, cmat_fname)
    
    
    
    



