function ROI_calc_matrix(WD,SUB_LIST)
% calculate the connectivity and correlation matrix
% load_nii_hdr modified to support .gz files

% Load the subject list
SUB_LIST=textread(SUB_LIST,'%s');


for i = 1:length(SUB_LIST)
    sub_LISTCreateMatrix(WD,SUB_LIST{i})
end



function sub_LISTCreateMatrix(WD, SUB)
% sub_LISTCreateMatrix
% Purpose: 
%   Generates matrices in .mat format for each ROI in each subject.
%
% Inputs: 
%   - WD (string): Path to the working directory containing the subject's data.
%   - SUB (string): Subject ID to specify which data to process (foldername of the subject).

    % Retrieve the list of ROI masks from the specified folder
    roi_list = dir(fullfile(WD, SUB, 'ROI_masks'));
    
    % Skip the '.' and '..' entries
    roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
    
    % Loop through each ROI mask in the list
    for j = 1:length(roi_list)
        
        % Construct the full path to the ROI mask file
        file = fullfile(roi_list(j).folder, roi_list(j).name);
        
        % Extract the file name without extension
        split_file = strsplit(roi_list(j).name, '.');
        fileName = split_file{1};
        
        % Load the coordinates for the ROI
        coord = load(fullfile(WD, SUB, 'ROI_masks_Coords', [fileName, '_coords.txt']));
        
        % Define the folder paths for the probtrackx output and the output matrices
        probtrackx_folder = fullfile(WD, SUB, [fileName, '_probtrackx']);
        outfolder = fullfile(WD, SUB, [fileName, '_matrix']);
        
        % Create the output folder if it doesn't already exist
        if ~exist(outfolder, 'dir')
            mkdir(outfolder);
        end
        
        % Generate the matrix using the loaded coordinates and probtrackx data
        f_Create_Matrix_v3_gpu(probtrackx_folder, outfolder, coord);
    end