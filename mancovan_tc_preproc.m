function mancovan_tc_preproc(mancovanInfo, step)


icatb_defaults;
global MANCOVA_DEFAULTS;

if (~exist('mancovanInfo', 'var') || isempty(mancovanInfo))
    mancovanInfo = icatb_selectEntry('title', 'Select Mancovan Parameter File', 'typeEntity', 'file', 'typeSelection', 'single', 'filter', '*mancovan.mat');
    if (isempty(mancovanInfo))
        error('Mancovan parameter file is not selected');
    end
    drawnow;
end


if (ischar(mancovanInfo))
    mancovaParamFile = mancovanInfo;
    clear mancovanInfo;
    load(mancovaParamFile);
    outputDir = fileparts(mancovaParamFile);
    if (isempty(outputDir))
        outputDir = pwd;
    end
    mancovanInfo.outputDir = outputDir;
else
    mancovanInfo.outputDir = mancovanInfo.userInput.outputDir;
end


if (~exist('step', 'var'))
    step = 1;
end

cd(mancovanInfo.outputDir);

logFile = fullfile(mancovanInfo.outputDir, [mancovanInfo.prefix, '_mancovan_results.log']);
tic;
diary(logFile);

%mancovanInfo.numOfSub = mancovanInfo.userInput.numOfSub;
mancovanInfo.comp = mancovanInfo.userInput.comp;
doEst = 0;
if (isfield(mancovanInfo.userInput, 'doEstimation'))
    doEst = mancovanInfo.userInput.doEstimation;
end
mancovanInfo.doEstimation = doEst;
mancovanInfo.numOfPCs = mancovanInfo.userInput.numOfPCs;
mancovanInfo.features = mancovanInfo.userInput.features;
if (length(mancovanInfo.numOfPCs) == 1)
    mancovanInfo.numOfPCs = repmat(mancovanInfo.numOfPCs, 1, length(mancovanInfo.features));
    mancovanInfo.userInput.numOfPCs = mancovanInfo.numOfPCs;
end
TR = mancovanInfo.userInput.TR;
mancovanInfo.prefix = mancovanInfo.userInput.prefix;
mancovanInfo.modelInteractions = mancovanInfo.userInput.modelInteractions;
mancovanInfo.comps = [mancovanInfo.comp.value];
mancovanInfo.comps = mancovanInfo.comps(:)';
step_P = mancovanInfo.userInput.p_threshold;
if (~isfield(mancovanInfo.userInput, 'feature_params'))
    feature_params = icatb_mancovan_feature_options('tr', TR, 'mask_dims', mancovanInfo.userInput.HInfo(1).dim(1:3));
    out = icatb_OptionsWindow(feature_params.inputParameters, feature_params.defaults, 'off', 'title', 'Feature Options');
    feature_params.final = out.results;
    clear out;
else
    feature_params = mancovanInfo.userInput.feature_params;
end

def_mask_stat = 't';
def_mask_z_thresh = 1;
try
    def_mask_stat = lower(feature_params.final.stat_threshold_maps);
    def_mask_z_thresh = feature_params.final.z_threshold_maps;
catch
end

def_mask_t_std = 4;
try
    def_mask_t_std = MANCOVA_DEFAULTS.sm.t_std;
catch
end

% Only positive voxels
t_image_values = 2;

try
    t_image_values = MANCOVA_DEFAULTS.sm.t_image_values;
catch
end

load(mancovanInfo.userInput.ica_param_file);
subjectICAFiles = icatb_parseOutputFiles('icaOutputFiles', sesInfo.icaOutputFiles, 'numOfSub', sesInfo.numOfSub, 'numOfSess', sesInfo.numOfSess, 'flagTimePoints', sesInfo.flagTimePoints);
outDir = fileparts(mancovanInfo.userInput.ica_param_file);
sesInfo.outputDir = outDir;
fileIn = dir(fullfile(outDir, [sesInfo.calibrate_components_mat_file, '*.mat']));
filesToDelete = {};
if (length(fileIn) ~= sesInfo.numOfSub*sesInfo.numOfSess)
    disp('Uncompressing subject component files ...');
    filesToDelete = icatb_unZipSubjectMaps(sesInfo, subjectICAFiles);
end

if ((step == 1) || (step == 2))
    %% Compute features
    %% Load subject components and average components across runs
    
    tp = min(sesInfo.diffTimePoints);
    
    comp_inds = mancovanInfo.comps;
    
    features = mancovanInfo.features;
    Vol = sesInfo.HInfo.V(1);
    mancovanInfo.HInfo = Vol;
    
    outputFiles = repmat(struct('feature_name', '', 'filesInfo', ''), 1, length(features));
    
    disp('Computing features ...');
    fprintf('\n');
    
    for nF = 1:length(features)
        
        cF = features{nF};
        
        outputFiles(nF).feature_name = cF;

            
            dirName = 'fnc_stats';
            
            if (exist(fullfile(mancovanInfo.outputDir, dirName)) ~= 7)
                mkdir(mancovanInfo.outputDir, dirName);
            end
            
            disp(['Loading subject timecourses of components ...']);
            timecourses = icatb_loadComp(sesInfo, comp_inds, 'vars_to_load', 'tc', 'subjects', mancovanInfo.good_sub_inds, 'truncate_tp', 1, ...
                'subject_ica_files', subjectICAFiles, 'detrend_no', feature_params.final.fnc_tc_detrend);
            
            timecourses = reshape(timecourses, size(timecourses, 1), sesInfo.numOfSess, size(timecourses, length(size(timecourses)) - 1), length(comp_inds));
            timecourses = timecourses(:, :, 1:min(sesInfo.diffTimePoints), :);
            
            if (strcmpi(feature_params.final.fnc_tc_despike, 'yes') && strcmpi(feature_params.final.fnc_tc_filter, 'yes'))
                disp('Despiking and filtering timecourses ...');
            else
                if (strcmpi(feature_params.final.fnc_tc_despike, 'yes'))
                    disp('Despiking timecourses ...');
                elseif (strcmpi(feature_params.final.fnc_tc_filter, 'yes'))
                    disp('Filtering timecourses ...');
                end
            end
            
            for nSub = 1:size(timecourses, 1)
                for nSess = 1:sesInfo.numOfSess
                    for nComp = 1:length(comp_inds)
                        if (strcmpi(feature_params.final.fnc_tc_despike, 'yes'))
                            timecourses(nSub, nSess, :, nComp) = icatb_despike_tc(timecourses(nSub, nSess, :, nComp), TR);
                        end
                        if (strcmpi(feature_params.final.fnc_tc_filter, 'yes'))
                            timecourses(nSub, nSess, :, nComp) = icatb_filt_data(timecourses(nSub, nSess, :, nComp), TR);
                        end
                    end
                    c = icatb_corr(squeeze(timecourses(nSub, nSess, :, :)));
                    c(1:size(c, 1) + 1:end) = 0;
                    c = icatb_mat2vec(icatb_r_to_z(c));
                    if ((nSub == 1) && (nSess == 1))
                        fnc_corrs = zeros(size(timecourses, 1), sesInfo.numOfSess, numel(c));
                    end
                    fnc_corrs(nSub, nSess, :) = c(:)';
                end
            end
            
            fnc_corrs_all = fnc_corrs;
                        if (mancovanInfo.doEstimation)
                comp_est = order_selection(fnc_corrs);
            else
                comp_est = mancovanInfo.numOfPCs(strmatch(cF, lower(mancovanInfo.features), 'exact'));
            end
            
            resultsFile = fullfile(dirName, [mancovanInfo.prefix, '_results_fnc.mat']);
            comp_number = comp_inds;
            disp(['Saving file ', resultsFile, ' ...']);
            
            result_files{1} = resultsFile;
            
            icatb_save(fullfile(mancovanInfo.outputDir, resultsFile), 'comp_est', 'comp_number', 'fnc_corrs', 'fnc_corrs_all');
            tc_preproc = permute(timecourses,[3,4,2,1])
            timecourseFile = [mancovanInfo.prefix, '_preproc_timecourses.mat'];    
            icatb_save(fullfile(mancovanInfo.outputDir, timecourseFile), 'tc_preproc');
    end
end



    
