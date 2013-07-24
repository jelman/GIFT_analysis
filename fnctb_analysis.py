import os, sys
sys.path.insert(0, '/home/jagust/jelman/CODE/GIFT_analysis')
import gift_output as gift
from glob import glob
import numpy as np

datadir = '/home/jagust/rsfmri_ica/GIFT/GICA_d30/FNCtb'
fnctb_info = 'GraphAndData.mat'
fnc_corr_out = 'fnc_corr.csv'
fnc_lag_out = 'fnc_lag.csv'


infile = os.path.join(datadir, fnctb_info)

fnc_corr, fnc_lag = gift.fnctb_stats(infile)

fnc_corr_outfile = os.path.join(datadir, fnc_corr_out)
np.savetxt(fnc_corr_outfile, fnc_corr, delimiter='\t')
fnc_lag_outfile = os.path.join(datadir, fnc_lag_out)
np.savetxt(fnc_lag_outfile, fnc_lag, delimiter='\t')
