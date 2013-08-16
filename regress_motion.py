import os, sys
import shutil
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
sys.path.insert(0, '/home/jagust/jelman/CODE/misc')
import general_utilities as utils
import gift_utils as gu


def backup_data(datadir, globstr):
    """
    back up all files in datadir matching pattern specified by globstr
    """
    backupdir = utils.make_dir(icadir, 'tc_backup')
    tc_files = glob(os.path.join(icadir,tc_glob))
    for src in tc_files:
        try:
            shutil.copy(src,backupdir)
        except:
            raise IOError('%s not copies'%src)
    
    
    
def main():
    backup_data(datadir, tc_glob)    
    
if __name__ == '__main__':
    
    ##### Set parameters ##########
    icadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30'
    datadir = '/home/jagust/rsfmri_ica/GIFT/data'
    tc_glob = '*_sub*_timecourses_ica_s1_.nii'
    
    ################################
    
    
    
    



