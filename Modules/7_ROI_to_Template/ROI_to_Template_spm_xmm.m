function ROI_to_Template_spm_xmm(WD,SUB_LIST,MAX_CL_NUM,VOX_SIZE,METHOD)
%-----------------------------------------------------------------------
% transform ROIs from DTI(b0) space to MNI space
%-----------------------------------------------------------------------

SUB = textread(SUB_LIST,'%s');

fprintf('Processing ROI to Template\n');
fprintf('Method: %s\n',METHOD);

roi_list = dir(strcat(WD, '/ROI_masks'));
% Skip the '.' and '..' entries
roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
for j = 1:length(roi_list)
	% Get the name of the file
	split_file=strsplit(roi_list(j).name, '.');
	fileName = split_file{1};
    for i=1:length(SUB)
		spm_norm_ew(WD,SUB,i,fileName,MAX_CL_NUM,METHOD,VOX_SIZE)
    end
	matlabbatch=[];
end

function spm_norm_ew(WD,SUB,i,ROI,MAX_CL_NUM,METHOD,VOX_SIZE)
%-----------------------------------------------------------------------
% transforms the clustered ROI from DTI(b0) space to MNI space using the deformation field
%-----------------------------------------------------------------------


	% Path to the subject's folder
	sourcepath=strcat(WD,'/',SUB{i});

	% Path to the deformation field
	def = fullfile(sourcepath,['DTI_to_MNI_deformation_field_', SUB{i},'.nii']);

	for N=2:MAX_CL_NUM
		resampleimg{N}=strcat(sourcepath,'/',SUB{i},'_',ROI,'_',METHOD,'/',SUB{i},'_',ROI,num2str(N),'.nii');
	end

	spm('defaults','fmri');
	spm_jobman('initcfg');

	for N = 2:MAX_CL_NUM
	
		matlabbatch{1}.spm.spatial.normalise.write.subj.def = {def};
		matlabbatch{1}.spm.spatial.normalise.write.subj.resample = {resampleimg{N}};
		matlabbatch{1}.spm.spatial.normalise.write.woptions.bb = [-90 -126 -72
                                                          			90 90 108];
		matlabbatch{1}.spm.spatial.normalise.write.woptions.vox = [VOX_SIZE VOX_SIZE VOX_SIZE];
		matlabbatch{1}.spm.spatial.normalise.write.woptions.interp = 0;
		matlabbatch{1}.spm.spatial.normalise.write.woptions.prefix = 'w';

 		spm_jobman('run',matlabbatch)
	end
	
	disp(strcat(SUB{i},' Done!'));