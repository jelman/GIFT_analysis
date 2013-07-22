import os, sys
from glob import glob
sys.path.insert(0, '/home/jagust/jelman/CODE/connectivity/ica')
import python_dual_regress as pydr
import commands
from nipype.interfaces.base import CommandLine

if __name__ == '__main__':

    if len(sys.argv) ==1:
        print 'USAGE: python create_4d_icfiles.py <basedir>'
        print 'basedir should contain GIFT components files'
    else:
        args = sys.argv[1]
        
    ###### Set paths and patterns #########    
    basedir = args
    outdir = os.path.join(basedir, 'ic_files')
    subic_globstr = os.path.join(basedir, '*sub*_component_ica_s1_.nii') # search string for sub ic files
    ic4d_globstr = os.path.join(outdir, 'dr_stage2_ic*_4D.nii.gz')
    subid_pattern = u'sub[0-9]{3}'
    #######################################

    # Make output directory
    if os.path.isdir(outdir)==False:
        os.mkdir(outdir)
    else:
        raise OSError('%s exists, remove to re-run'%outdir)

    # Split files of each subject containing all ic's
    infiles = glob(subic_globstr)
    for subfile in infiles:
        subid = pydr.get_subid(subfile, pattern=subid_pattern)
        allic = pydr.split_components(subfile, subid, outdir)
    
    # Merge files of each ic across subjects  
    for cn, item in enumerate(allic): #Search through ics using last subject's output
        datadir, ic = os.path.split(item)       
        subid = pydr.get_subid(item, pattern=subid_pattern)
        globstr = ic.replace(subid, '*')
        mergefile, subject_order = pydr.merge_components(datadir,
                                                      globstr = globstr,
                                                      subid_pattern = subid_pattern)
        outfile = os.path.join(outdir, 'subject_order_ic%04d'%cn)
        with open(outfile, 'w+') as fid: 
            fid.write('\n'.join(subject_order)) #Write out subject order for each ic
    
    # Rename files with ic count starting at 1 and unzip      
    for cn, item in enumerate(glob(ic4d_globstr)):
        datadir, filename = os.path.split(item)
        new_cn = cn + 1
        newfile = os.path.join(datadir, ''.join(['ic','%03d'%new_cn, '_4D.nii.gz']))
        os.rename(item, newfile)
        cmd = CommandLine('gunzip %s'%(newfile))
        cmd.run()
        order_file = os.path.join(datadir, 'subject_order_ic%04d'%cn)
        new_order_file = os.path.join(datadir, 'subject_order_ic%03d'%new_cn)
        os.rename(order_file, new_order_file)

