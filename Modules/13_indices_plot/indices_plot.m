function indices_plot(PWD,SUB_LIST,VOX_SIZE,MAX_CL_NUM,split_half,tpd)

if tpd==1
    % Get the list of ROIs
    roi_list = dir(fullfile(PWD, 'ROI_masks'));
    roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
    % Create a list of all combinations of the items in roi_list
    combinations = nchoosek(1:length(roi_list), 2);
    
    % Iterate over each combination
    for k = 1:size(combinations, 1)
        ROI1 = strsplit(roi_list(combinations(k, 1)).name, '.');
        ROI1 = ROI1{1};
        ROI2 = strsplit(roi_list(combinations(k, 2)).name, '.');
        ROI2 = ROI2{1};
        plot_tpd(PWD,SUB_LIST,VOX_SIZE,MAX_CL_NUM, ROI1, ROI2)

    end
end

if split_half==1
    % Get the list of ROIs
    roi_list = dir(fullfile(PWD, 'ROI_masks'));
    roi_list = roi_list(~ismember({roi_list.name}, {'.', '..'}));
    % Write the header row with ROI names
    
    for j = 1:length(roi_list)
        split_file = strsplit(roi_list(j).name, '.');
        fileName = split_file{1};
        plot_split_half(PWD,fileName,SUB_LIST,VOX_SIZE,MAX_CL_NUM);
    end  
end
