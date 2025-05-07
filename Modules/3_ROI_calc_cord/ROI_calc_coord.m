function ROI_calc_coord(WD, SUB_LIST, POOLSIZE, type)
% Calculate coordinates of the voxels in the ROI in DTI space and save the volumes in a csv file

% Read the list of subjects
SUB = textread(SUB_LIST, '%s');

% Open the CSV file for writing ROI volumes
sizeFile = fopen(fullfile(WD, strcat(type, '_volumes.csv')), 'w');
fprintf(sizeFile, 'subject');

% Get the list of ROIs
roi_list = dir(fullfile(WD, type));
roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));

% Write the header row with ROI names
for j = 1:length(roi_list)
    split_file = strsplit(roi_list(j).name, '.');
    fileName = split_file{1};
	disp(fileName)
    fprintf(sizeFile, ',%s', fileName);
end
fprintf(sizeFile, '\n');

% Process each subject
for i = 1:length(SUB)
    fprintf(sizeFile, '%s', SUB{i});
    roi_dir = fullfile(WD, SUB{i}, type);
    
    % Create the ROI_Coords directory if it doesn't exist
    output_dir = fullfile(WD, SUB{i}, strcat(type, '_Coords'));
    if ~exist(output_dir, 'dir')
        mkdir(output_dir);
    end
    % Get the list of ROIs for this subject
    roi_list = dir(fullfile(roi_dir, '*.nii*'));
    roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
    
    
    % Process each ROI
    for j = 1:length(roi_list)
        % Load the ROI NIfTI file
        file = fullfile(roi_list(j).folder, roi_list(j).name);
        fprintf(file);
        roi = load_untouch_nii(file);
        roi.img(isnan(roi.img)) = 0;
        [nxl, nyl, nzl] = size(roi.img);
        
        % Extract the base filename (without extension)
        split_file = strsplit(roi_list(j).name, '.');
        fileName = split_file{1};
        
        % Open the coordinate file for writing
        fid = fopen(fullfile(output_dir, [fileName, '_coords.txt']), 'w');
        
        % Find and write the coordinates of voxels
        voxelCount = 0;
        for zl = 1:nzl
            [xl, yl] = find(roi.img(:, :, zl) ~= 0);
            for k = 1:numel(xl)
                fprintf(fid, '%d %d %d\r\n', xl(k)-1, yl(k)-1, zl-1);
                voxelCount = voxelCount + 1;
            end
        end
        fclose(fid);
        
        % Write the voxel count to the CSV file
        fprintf(sizeFile, ',%d', voxelCount);
        
        % Save the modified NIfTI file
        save_untouch_nii(roi, file);
        
        disp([SUB{i}, '/', fileName, ' Done!']);
    end
    fprintf(sizeFile, '\n');
end

% Close the CSV file
fclose(sizeFile);

end


