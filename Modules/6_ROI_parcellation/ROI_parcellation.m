function ROI_parcellation(WD,SUB_LIST,MAX_CL_NUM,METHOD)
% ROI parcellation based on spectral clustering of the correlation matrix (similarity matrix)

SUB = textread(SUB_LIST,'%s');


N = MAX_CL_NUM-1;

% Loop through each subject in SUB list
for i = 1:length(SUB)
    % Get the list of ROIs for the current subject
    roi_list = dir(fullfile(WD, SUB{i}, 'ROI_masks'));
    
    % Skip the '.' and '..' entries
    roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
    
    % Loop through each ROI in the list
    for j = 1:length(roi_list)
        % Get the name of the ROI (without the extension)
        split_file = strsplit(roi_list(j).name, '.');
        roi_name = split_file{1};
        
        % Define the output directory path
        outdir = fullfile(WD, SUB{i}, [roi_name, '_', METHOD]);

        % Create the output directory if it doesn't exist
        if ~exist(outdir, 'dir');mkdir(outdir);end
        
        % Load the necessary variables (coordinates and matrix) from the ROI's matrix file
        data = load(fullfile(WD, SUB{i}, [roi_name, '_matrix'], 'connection_matrix.mat'), 'xyz', 'matrix');
        coordinates = data.xyz;
        matrix = data.matrix;

        panduan = any(matrix');
	    coordinates = coordinates(panduan,:);
	    matrix = matrix(panduan,:);

        % Load the ROI image file
        nii = load_untouch_nii(fullfile(WD, SUB{i}, 'ROI_masks', roi_list(j).name));
        image_f = nii.img;

        % Loop through each of the N clusters (or other parameter depending on the method)
        for k = 1:N
            % Define the output file name for the current cluster
            filename = fullfile(outdir, [roi_name, num2str(k+1), '.nii']);
            
            % Check if the file already exists
            if ~exist(filename, 'file')
                display([roi_name, '_', num2str(k+1), ' processing...']);
                
                % Switch case based on the chosen clustering method
                switch METHOD
                    case 'sc'
                        % Using sc3 clustering method
                        fprintf('Using sc3\n');

						% Calculate the correlation matrix (similarity matrix) for spectral clustering
                        matrix1 = matrix * matrix';
                        matrix1 = matrix1 - diag(diag(matrix1)); % Remove diagonal elements
                        output = fullfile(WD, SUB{i}, [roi_name, '_matrix'], 'correlation_matrix.mat');
                        fprintf('Saving correlation matrix\n');
                        save(output, 'matrix1', 'coordinates', '-v7.3');
                        
                        % Perform clustering
                        index = sc3(k+1, matrix1);
                        
					% Add support for other clustering methods here if needed
					% case 'kmeans'
					%     index = kmeans(matrix, k+1, 'Replicates', 300);
					% case 'simlr'
					%     addpath('SIMLR');
					%     index = SIMLR_Cluster(k+1, matrix);

                    otherwise
                        error('Error: Unknown clustering method!');
                end

                % Initialize the cluster nifti
                image_f(:,:,:) = 0;
                
                % Assign the cluster indices to the coordinates in the image
                for j = 1:length(coordinates)
                    image_f(coordinates(j, 1) + 1, coordinates(j, 2) + 1, coordinates(j, 3) + 1) = index(j);
                end
                
                % Save the modified image to the output file
                nii.img = image_f;
                save_untouch_nii(nii, filename);
            end
        end
        
        % Display completion message for the current ROI
        fprintf([roi_name, ' Done!']);
    end
end


