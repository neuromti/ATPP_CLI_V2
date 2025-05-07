function cluster_relabel_group_xmm(PWD,ROI,SUB_LIST,MAX_CL_NUM,GROUP_THRES,METHOD,VOX_SIZE)
% relabel the clusters in each of the subjects to match the group image

SUB = textread(SUB_LIST,'%s');

GROUP_THRES=GROUP_THRES*100;

for CL_NUM=2:MAX_CL_NUM
    disp(strcat(ROI,'_cluster_',num2str(CL_NUM),' processing...'));
    REFER = fullfile(PWD,['group_',num2str(length(SUB)),'_',num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_',ROI,'_',num2str(CL_NUM),'_',num2str(GROUP_THRES),'_group.nii.gz']);
    vnii_stand = load_untouch_nii(REFER); 
    standard_cluster= vnii_stand.img;
    standard_cluster(isnan(standard_cluster))=0;
    sub_num=length(SUB);

	for i=1:sub_num
	    vnii=load_untouch_nii(fullfile(PWD,SUB{i},[SUB{i},'_',ROI,'_',METHOD],[num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_', SUB{i}, '_', ROI,num2str(CL_NUM),'_Template.nii.gz'])); 
	    tha_seg_result= vnii.img;
	    tha_seg_result(isnan(tha_seg_result))=0;
	    tmp_overlay=zeros(CL_NUM,CL_NUM);

	    for ki=1:CL_NUM
	        for kj=1:CL_NUM
	              tmp=(standard_cluster==ki).*(tha_seg_result==kj);
	              tmp_overlay(ki,kj)=sum(tmp(:));
	        end
	    end

	    [cind,max]=munkres(-tmp_overlay);

	    tmp_matrix=tha_seg_result;

	    for ki=1:CL_NUM
	        tmp_matrix(tha_seg_result==cind(ki))=ki;
	    end
	    vnii.img=tmp_matrix;
	    save_untouch_nii(vnii,fullfile(PWD,SUB{i},[SUB{i},'_',ROI,'_',METHOD],[num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_',ROI,'_',num2str(CL_NUM),'_Template_relabel_group.nii.gz']));

	    disp(strcat('relabeled for subject : ',SUB{i},' kc=',num2str(CL_NUM)));
	end
end
