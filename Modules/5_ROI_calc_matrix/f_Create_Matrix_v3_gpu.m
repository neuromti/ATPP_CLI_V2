function f_Create_Matrix_v3_gpu(imgfolder,outfolder,coord)
% Removes the 0 and nan values from the connection matrix and saves it as a .mat file

% Get the path to fdt_matrix2.dot
file_path = strcat(imgfolder,'/fdt_matrix2.dot');

% Load Matrix2  
x=load(file_path);  

%con_matrix=full(spconvert(x));  
con_matrix= spconvert(x);  

fprintf('Remove 0 or NaN columns ...\n');
% Step 1: Replace NaN and Inf values with 0
con_matrix(isnan(con_matrix) | isinf(con_matrix)) = 0;
% Step 3: Remove columns that are entirely zeros
col_removal = any(con_matrix, 1);  % Returns true for columns with at least one non-zero element
con_matrix = con_matrix(:, col_removal);  % Keep only columns with non-zero values
% Sparse to full 
con_matrix = full(con_matrix);

% Safe the connection matrix
fprintf('Safe connection_matrix...\n');
output = strcat(outfolder,'/connection_matrix.mat');

% Rename the variables for proper matrix names
matrix = con_matrix;
xyz = coord;

save(output,'matrix','xyz','-v7.3');
clear con_matrix;
clear matrix;