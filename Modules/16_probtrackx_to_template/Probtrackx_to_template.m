function Probtrackx_to_template(WD, SUB_LIST, VOX_SIZE, NORMALIZE)
    % Load subject list
    subject_list = textread(SUB_LIST, '%s');
    % Print all arguments
    fprintf('Working Directory: %s\n', WD);
    fprintf('Subject List File: %s\n', SUB_LIST);
    fprintf('Voxel Size: %d\n', VOX_SIZE);
    fprintf('Normalize: %s\n', NORMALIZE);
    VOX_SIZE=1;

    % Start parallel pool
    if isempty(gcp('nocreate'))
        parpool;
    end
    
    % Parallelize over subjects
    parfor i = 1:length(subject_list)
        SUB = subject_list{i};
        
        % Get ROI masks
        roi_list = dir(fullfile(WD, SUB, 'ROI_masks', '*.nii*'));
        roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
        
        % Get Target masks
        target_list = dir(fullfile(WD, SUB, 'Target_masks', '*.nii*'));
        target_list = target_list(~ismember({target_list.name}, {'.', '..'}));

        % Iterate normally over ROI and Targets inside each subject
        for j = 1:length(roi_list)
            file = fullfile(roi_list(j).folder, roi_list(j).name);
            split_file = strsplit(roi_list(j).name, '.');
            fileName = split_file{1};
            FOLDER = strcat(fileName, '_probtrackx');

            for k = 1:length(target_list)
                split_target_file = strsplit(target_list(k).name, '.');
                TARGET = split_target_file{1};

                %% Run function
                %sourcepath = strcat(WD, '/', SUB);
                %output_file =  fullfile(sourcepath, FOLDER, ['template_seeds_to_', TARGET, '.nii']);
                %if exist(output_file, 'file')
                %    disp(['Skipping ', output_file, ' as it already exists.']);
                %    continue;
                %end
                spm_norm_ew(WD, SUB, FOLDER, fileName, VOX_SIZE, NORMALIZE, TARGET);
            end
        end
    end
    
    disp('All subjects processed!');
end




function spm_norm_ew(WD, SUB, FOLDER, ROI, VOX_SIZE, NORMALIZE, TARGET)
    sourcepath = strcat(WD, '/', SUB);
    disp(sourcepath);
    
    % Assuming the deformation field 'y_' file exists in the same directory as your T1 images
    def = strcat(sourcepath, '/DTI_to_MNI_deformation_field_', SUB, '.nii');
    
    % Define the path to your ROI file
    gunzip(fullfile(sourcepath, FOLDER, ['seeds_to_', TARGET, '.nii.gz']));
    disp(fullfile(sourcepath, FOLDER, ['seeds_to_', TARGET, '.nii.gz']))
    roiimg = fullfile(sourcepath, FOLDER, ['seeds_to_', TARGET, '.nii']);
    
    spm('defaults', 'fmri');
    spm_jobman('initcfg');
    fprintf('VOX_SIZE = %d\n', VOX_SIZE);
    
    matlabbatch{1}.spm.spatial.normalise.write.subj.def = {def};
    matlabbatch{1}.spm.spatial.normalise.write.subj.resample = {roiimg};
    matlabbatch{1}.spm.spatial.normalise.write.woptions.bb = [-78 -112 -70; 78 76 85];
    matlabbatch{1}.spm.spatial.normalise.write.woptions.vox = [VOX_SIZE VOX_SIZE VOX_SIZE];
    matlabbatch{1}.spm.spatial.normalise.write.woptions.interp = 0; % Using 4th degree B-spline interpolation
    matlabbatch{1}.spm.spatial.normalise.write.woptions.prefix = 'template_';
    

    spm_jobman('run', matlabbatch);
    
    
    % Remove the SubjectID
    ROI_name = strrep(ROI, [SUB, '_'], '');
    outputfolder = fullfile(WD, [ROI_name, '_templatespace_connectivity']);
    if ~isfolder(outputfolder)
        mkdir(outputfolder);
    end
    % After normalization, rename and move the output file
    normalized_file = fullfile(sourcepath, FOLDER, ['template_seeds_to_', TARGET, '.nii']);
    % Remove NaN-Value from the image
    roi = load_untouch_nii(normalized_file);
	roi.img(isnan(roi.img))=0;
    %disp(['NORMALIZE = ', num2str(NORMALIZE)]);
    %Normalize the connectivity by clustersize
    if NORMALIZE == '1'
        disp(['NORMALIZE = ', num2str(NORMALIZE)]);
        csvpath = fullfile(WD, 'roi_volumes.csv')
        clustersizes = readtable(csvpath);
        disp(clustersizes);
        disp(ROI_name);
        rowIndex = find(clustersizes.('subject') == str2num(SUB));
        clustersize = clustersizes.(ROI_name)(rowIndex);
        disp(clustersize);
        roi.img = roi.img / clustersize;
    end
    save_untouch_nii(roi,normalized_file)
    %movefile(normalized_file, outputfolder);

    disp(strcat('Normalization of ', ROI_name, ' for ', SUB, ' done!'));
end

