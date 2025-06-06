function postprocess_mpm_group_xmm(PWD,ROI,SUB_LIST,MAX_CL_NUM,MPM_THRES,VOX_SIZE)

SUB=textread(SUB_LIST,'%s');

disp(strcat('Running postprocess for <',ROI,'> ...'));	

MPM_THRES = MPM_THRES * 100;
path = strcat(PWD,'/MPM_',num2str(length(SUB)),'_',num2str(VOX_SIZE),'mm/');

for CL_NUM=2:MAX_CL_NUM
    filename = strcat(num2str(VOX_SIZE),'mm_',ROI,'_',num2str(CL_NUM),'_MPM_thr',num2str(MPM_THRES),'_group.nii.gz');
    info = load_untouch_nii(strcat(path,filename));
    img = info.img;
    img(isnan(img))=0;
    [m n p] = size(img);
    coordinates = zeros(0,0);
    z = 1;
    for i = 1:m
        for j = 1:n
            for k = 1:p
                if img(i,j,k) ~= 0
                   coordinates(z,1) = i;
                   coordinates(z,2) = j;
                   coordinates(z,3) = k;
                   z = z + 1;
                end
            end
        end
    end
    for i = 1:length(coordinates)
        label = zeros(1,CL_NUM + 1);
        label_value1 = img(coordinates(i,1)-1,coordinates(i,2),coordinates(i,3)) + 1;
        label(label_value1) = label(label_value1) + 1;
        
        label_value2 = img(coordinates(i,1)+1,coordinates(i,2),coordinates(i,3)) + 1;
        label(label_value2) = label(label_value2) + 1;
        
        label_value3 = img(coordinates(i,1),coordinates(i,2)-1,coordinates(i,3)) + 1;
        label(label_value3) = label(label_value3) + 1;
        
        label_value4 = img(coordinates(i,1),coordinates(i,2)+1,coordinates(i,3)) + 1;
        label(label_value4) = label(label_value4) + 1;
        
        label_value5 = img(coordinates(i,1),coordinates(i,2),coordinates(i,3)-1) + 1;
        label(label_value5) = label(label_value5) + 1;
        
        label_value6 = img(coordinates(i,1),coordinates(i,2),coordinates(i,3)+1) + 1;
        label(label_value6) = label(label_value6) + 1;
        
        wjs = max(label); 
        if wjs >= 3 % majority voting
            jsh = find(label == wjs);
            if length(jsh)>=2
                b = jsh(1,2) - 1;
            else
                b = jsh - 1;
            end
        img(coordinates(i,1),coordinates(i,2),coordinates(i,3)) = b;
        end
    end
    img_MPM = img;
    info = load_untouch_nii(strcat(path,filename));
    info.img = img_MPM;
    output = strcat(num2str(VOX_SIZE),'mm_',ROI,'_',num2str(CL_NUM),'_MPM_thr',num2str(MPM_THRES),'_group_smoothed.nii.gz');
    save_untouch_nii(info,strcat(path,output));
    disp(strcat(ROI,'_',num2str(CL_NUM),' Done!'));
end
