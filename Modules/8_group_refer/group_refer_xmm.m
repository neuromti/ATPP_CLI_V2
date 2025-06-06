function group_refer_xmm(PWD,ROI,SUB_LIST,MAX_CL_NUM,METHOD,VOX_SIZE,GROUP_THRES)
% calculate symmetric group reference images to prepare for the relabel step

SUB = textread(SUB_LIST,'%s');
subnum = length(SUB);

if GROUP_THRES == 0
	GROUP_THRES_REAL=eps;
else
	GROUP_THRES_REAL=GROUP_THRES;
end


% Make a group reference image in MNI space that outlines the SN mask in MNI space based on the group threshold
defnii = load_untouch_nii(fullfile(PWD,SUB{1},[SUB{1},'_',ROI,'_',METHOD], ...
									[num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_',SUB{1}, '_' ,ROI,num2str(2),'_Template.nii.gz']));
sumimg = zeros(size(defnii.img));
for j = 1:subnum 
	disp(strcat(SUB{j}));
	datanii = load_untouch_nii(fullfile(PWD,SUB{j},[SUB{j},'_',ROI,'_',METHOD], ...
								[num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_',SUB{j}, '_' ,ROI,num2str(2),'_Template.nii.gz']));

	datanii.img(isnan(datanii.img))=0;
	datanii.img(datanii.img>0) = 1;
	datanii.img=double(datanii.img);
	sumimg = sumimg + datanii.img;
end

defimg = sumimg;
defimg(defimg<GROUP_THRES_REAL*subnum)=0;
defimg(defimg>0)=1;
defnii.img = defimg;
grouproipath = strcat(PWD, '/', 'group_',num2str(length(SUB)),'_',num2str(VOX_SIZE),'mm/');


if ~exist(grouproipath,'dir');mkdir(grouproipath);end

% Safe the group reference image
save_untouch_nii(defnii,strcat(grouproipath,ROI,'_roimask_thr',num2str(GROUP_THRES_REAL*100),'.nii.gz'));

roiindex = find(sumimg >= GROUP_THRES_REAL*subnum);
ROISIZE = length(roiindex);


for CL_NUM=2:MAX_CL_NUM 
    disp(strcat(ROI, ' cluster number_',num2str(CL_NUM),' is running...'));
	groupmatrix = zeros(ROISIZE,ROISIZE);

	for j = 1:length(SUB)
		datanii = load_untouch_nii(fullfile(PWD,SUB{j},[SUB{j},'_',ROI,'_',METHOD] , [num2str(VOX_SIZE),'mm'],[num2str(VOX_SIZE),'mm_',SUB{j}, '_',ROI,num2str(CL_NUM),'_Template.nii.gz']));
		dataimg = double(datanii.img);
		dataimg(isnan(dataimg))=0;
		kimatrix=zeros(ROISIZE,ROISIZE);

		for ki=1:CL_NUM
			kimatrix(:)=0;
			kind = find(dataimg==ki);
		  	[tf,vind] = ismember(kind,roiindex);
			kimatrix(vind(vind>0),vind(vind>0)) = 1;
			groupmatrix = groupmatrix + kimatrix;
		end	
	end

	groupmatrix=groupmatrix-diag(diag(groupmatrix));
	index=sc3(CL_NUM,groupmatrix);
	
	img_f = zeros(size(defnii.img));
	a=1:1:length(index);
	img_f(roiindex(a)) = index(a);
	defnii.img = img_f;
	save_untouch_nii(defnii,strcat(grouproipath,num2str(VOX_SIZE),'mm_',ROI,'_',num2str(CL_NUM),'_',num2str(GROUP_THRES_REAL*100),'_group.nii.gz'));

	disp(strcat(ROI,' cluster number_',num2str(CL_NUM),' Done !!'));
end
