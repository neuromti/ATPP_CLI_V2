function ROI_registration_spm(WD,SUB_LIST,POOLSIZE, SPM)
%-----------------------------------------------------------------------
% transform ROIs from MNI space to DTI(b0) space
%-----------------------------------------------------------------------

SUB = textread(SUB_LIST,'%s');

% Parallel Computing Toolbox settings
% 2014a removed findResource, replaced by parcluster
% 2016b removed matlabpool, replaced by parpool

% modify temporary dir
temp_dir=tempname();
mkdir(temp_dir);
if exist('parcluster')
	pc=parcluster('local');
	pc.JobStorageLocation=temp_dir;
else
	sched=findResource('scheduler','type','local');
	sched.DataLocation=temp_dir;
end

% open pool
if exist('parpool')
	p=parpool('local',POOLSIZE);
else
	matlabpool('local',POOLSIZE);
end


matlabbatch=[];

% coregister T1 image to MNI space
parfor i=1:length(SUB)
	spm_norm_e(WD,SUB,i, SPM)
end
matlabbatch=[];

% Process ROIs
process_files(WD, SUB, 'ROI_masks');

% Process Exclusion masks
process_files(WD, SUB, 'Exclusion_masks');

% Process Stop masks
process_files(WD, SUB, 'Stop_masks');

% Process Target masks
process_files(WD, SUB, 'Target_masks');

% Process Waypoint masks
process_files(WD, SUB, 'Waypoint_masks');

% Function to tranforms masks from MNI to native space
function process_files(WD, SUB, folder_name)
	file_list = dir([WD, '/', folder_name]);

	% Skip the '.' and '..' entries
	file_list = file_list(~ismember({file_list.name}, {'.', '..'}));

	for i = 1:length(file_list)
		% Get the name of the file or folder
		file = strcat(file_list(i).folder, '/', file_list(i).name);
		convert_rois(file)
		disp(["Mask" ' ' num2str(i)]);
		disp(file_list(i).name);
		parfor j = 1:length(SUB)
			spm_util_deform(WD, SUB, j, file, folder_name)
		end
		matlabbatch = [];
	end

function spm_norm_e(WD,SUB,i, SPM)

	sourcepath = strcat(WD,'/',SUB{i});    
	
    fprintf('Normalizing T1 Native to MNI. T1 is: %s ',sourcepath);

	sourceimg = strcat(sourcepath,'/T1_in_diffusion_space_',SUB{i},'.nii');
	
	spm('defaults','FMRI');
	spm_jobman('initcfg');

	matlabbatch{1}.spm.spatial.normalise.est.subj.vol = {sourceimg};
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.biasreg = 0.0001;
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.biasfwhm = 60;
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.tpm = {[SPM, '/tpm/TPM.nii']};
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.affreg = 'mni';
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.reg = [0 0.001 0.5 0.05 0.2];
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.fwhm = 0;
	%% changed it to two for balance between accuracy and speed, if facing issue with memory maybe increase it 
	matlabbatch{1}.spm.spatial.normalise.est.eoptions.samp = 2;
	spm_jobman('run',matlabbatch)

function convert_rois(file)
    roi=load_untouch_nii(file);
    roi.hdr.dime.datatype=64;
    roi.hdr.dime.bitpix=64;
    roi.img=double(roi.img);
    save_untouch_nii(roi,file);	


function spm_util_deform(WD,SUB,i,ROI, outputfolder)
	sourcepath = strcat(WD,'/',SUB{i});
	if ~exist(strcat(sourcepath, '/', outputfolder), 'dir')
		mkdir(strcat(sourcepath, '/', outputfolder))
    end
	disp(sprintf('Warping masks from MNI to native %s ',sourcepath))

   	refimg = strcat(sourcepath,'/T1_in_diffusion_space_',SUB{i},'.nii');
	defimg = strcat(sourcepath,'/y_T1_in_diffusion_space_',SUB{i},'.nii');

	spm('defaults','FMRI');
	spm_jobman('initcfg');
	
	matlabbatch{1}.spm.util.defs.comp{1}.inv.comp{1}.def = {defimg};
	matlabbatch{1}.spm.util.defs.comp{1}.inv.space = {refimg};
	
	%%% this step didn't change anything, still include?
	matlabbatch{1}.spm.util.defs.comp{1}.inv.comp{1}.sn2def.vox = [NaN NaN NaN];
    matlabbatch{1}.spm.util.defs.comp{1}.inv.comp{1}.sn2def.bb = [NaN NaN NaN NaN NaN NaN];
    	%%%
    	
	matlabbatch{1}.spm.util.defs.out{1}.pull.fnames = {ROI};
	matlabbatch{1}.spm.util.defs.out{1}.pull.savedir.saveusr = {strcat(sourcepath, '/', outputfolder)};
	matlabbatch{1}.spm.util.defs.out{1}.pull.interp = 0;
	matlabbatch{1}.spm.util.defs.out{1}.pull.mask = 1;
	matlabbatch{1}.spm.util.defs.out{1}.pull.fwhm = [0 0 0];
	matlabbatch{1}.spm.util.defs.out{1}.pull.prefix = strcat(SUB{i},'_');                  
	
	spm_jobman('run',matlabbatch)
 




