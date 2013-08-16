import os, sys
import shutil
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
sys.path.insert(0, '/home/jagust/jelman/CODE/misc')
import general_utilities as utils
import gift_utils as gu
from glob import glob


def backup_data(datadir, filelist):
    """
    back up all files in datadir matching pattern specified by globstr
    """
    backupdir = utils.make_dir(icadir, 'tc_backup')
    for src in filelist:
        try:
            shutil.copy(src,backupdir)
        except:
            raise IOError('%s not copies'%src)
            
def find_sub_file(subid, filelist):
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


def main(icadir, datadir, tc_glob):
    tc_files = glob(os.path.join(icadir,tc_glob))
    backup_data(datadir, tc_files)  
    for subid in sorted(subid_map.keys()):
        subnum = subid_map[subid]
        subtc_file = find_sub_file(subnum, tc_files)
        subtc_dat, subtc_aff = utils.load_nii(sub_tc_file)
        sub_mcpars = load_mcpars(datadir, subid)
        sub_mcpars_full = gu.add_squares(sub_mcpars)
        betah, Yfitted, resid = gu.glm(sub_mcpars_full, subtc_dat)
        subtc_cleaned = save_nii(subtc_file, resid, subtc_aff)
        
if __name__ == '__main__':
    
    ##### Set parameters ##########
    icadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30' # Directory containing ica output
    datadir = '/home/jagust/rsfmri_ica/GIFT/data' # Directory containing pre-processed data
    tc_glob = '*_sub*_timecourses_ica_s1_.nii' # File name pattern to search for tc files
    ################################
    
    # Regress motion parameters out of component timecourses
    main(icadir, datadir, tc_glob)
    
    
    
    



