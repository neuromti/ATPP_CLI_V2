function T1_to_b0(WD,SUB_LIST,POOLSIZE,TEMPLATE)
%-----------------------------------------------------------------------
% transforms T1 to b0 space
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

% coregister T1 image to b0 space
parfor i=1:length(SUB)
	spm_norm_e(WD,SUB,i)
end 
matlabbatch=[];

function spm_norm_e(WD,SUB,i)
	sourcepath = strcat(WD,'/',SUB{i});
	disp(sourcepath);
	b0refimg = strcat(sourcepath,'/b0_',SUB{i},'.nii');
	T1sourceimg = strcat(sourcepath,'/T1_',SUB{i},'.nii');

	spm('defaults','fmri');
	spm_jobman('initcfg');

 	matlabbatch{1}.spm.spatial.coreg.estwrite.ref = {b0refimg};
    matlabbatch{1}.spm.spatial.coreg.estwrite.source = {T1sourceimg};
    matlabbatch{1}.spm.spatial.coreg.estwrite.other = {''};
	matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.cost_fun = 'nmi';
	matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.sep = [4 2];
	matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.tol = [0.002 0.002 0.002 0.0001 0.0001 0.0001 0.001 0.001 0.001 0.0001 0.0001 0.0001];
	matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.fwhm = [7 7];
	matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.interp = 1;
	matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.wrap = [0 0 0];
	matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.mask = 0;
	matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.prefix = 'r';

	spm_jobman('run',matlabbatch)
