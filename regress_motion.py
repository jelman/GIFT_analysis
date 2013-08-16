import os, sys
import shutil
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
sys.path.insert(0, '/home/jagust/jelman/CODE/misc')
import general_utilities as utils
import gift_utils as gu


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
    subfile = [x for x in filelist if subnum in x]
    return subfile[0]    
    
def main(icadir, datadir, tc_glob):
    tc_files = glob(os.path.join(icadir,tc_glob))
    backup_data(datadir, tc_files)  
    for subid in sorted(subid_map.keys()):
        subnum = subid_map[subid]
        subtc = find_sub_file(subnum, tc_files)
    
if __name__ == '__main__':
    
    ##### Set parameters ##########
    icadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30'
    datadir = '/home/jagust/rsfmri_ica/GIFT/data'
    tc_glob = '*_sub*_timecourses_ica_s1_.nii'
    
    ################################
    
    
    
    



