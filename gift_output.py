import scipy.io

def dfnc_analysis_info(infile):
    mat = scipy.io.loadmat(infile)
    comp_nums = mat['dfncInfo']['comps'][0][0][0]
    ncomps = len(comp_nums)
    nsubs = len(mat['dfncInfo']['outputFiles'][0][0][0])
    return comp_nums, ncomps, nsubs
    
def dfnc_dyn_stats(infile):
    mat = scipy.io.loadmat(infile)
    fnc_dyn = mat['FNCdyn']
    dyn_mean = fnc_dyn.mean(axis=0)
    dyn_std = fnc_dyn.std(axis=0)
    return dyn_mean, dyn_std

def dfnc_spectra_stats(infile):
    mat = scipy.io.loadmat(infile)
    spectra_fnc = mat['spectra_fnc']
    spectra_mean = spectra_fnc.mean(axis=0)
    spectra_std = spectra_fnc.std(axis=0)
    return spectra_mean, spectra_std
    
def fnctb_stats(infile):
    mat = scipy.io.loadmat(infile)
    fnc_corr = mat['adCorrAbs'][:,:,0]
    fnc_lag = mat['adCorrAbs'][:,:,1]
    return fnc_corr, fnc_lag
