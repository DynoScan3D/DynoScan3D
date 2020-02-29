clc
clear
% Code adapted from http://mesh.brown.edu/byo3d/source.html
% Set structured lighting parameters.
objName      = 'test'; % object name (should correspond to a data directory)
seqType      = 'Gray'; % structured light sequence type ('Gray' or 'bin')
dSampleProj  = 1;      % downsampling factor (i.e., min. system resolution)
projValue    = 255;    % Gray code intensity (Was at 128, gray, for actual code)
minContrast  = 0.2;    % minimum contrast threshold (for Gray code pattern)
screenIndex  = 2;      % index of projector display (1 = first, 2 = second, etc.)
frameDelay   = 0.5;    % frame delay (in seconds)

% Set reconstruction parameters.
dSamplePlot = 100;     % down-sampling rate for Matlab point cloud display
distReject  = Inf;     % rejection distance (for outlier removal)
saveResults = true;    % enable/disable results output

% proj is 1920*1080 for this

width = input('Input the projector resolution width: ');
height = input('Input the projector resolution height: ');
rect = [ 0, 0, width, height];
   
% Generate vertical and horizontal Gray code stripe patterns.
% Note: P{j} contains the Gray code patterns for "orientation" j.
%       offset(j) is the integer column/row offset for P{j}.
if ~exist('I','var') || ~exist('J','var')
   if strcmp(seqType,'Gray')
      [P,offset] = graycode(width/dSampleProj,height/dSampleProj);
   else
      [P,offset] = bincode(width/dSampleProj,height/dSampleProj);
   end
   I = {}; J = {};
   for j = 1:2
      for i = 1:size(P{j},3)
         I{j,i} = projValue*imresize(P{j}(:,:,i),dSampleProj);
         J{j,i} = projValue*imresize(1-P{j}(:,:,i),dSampleProj);
      end
   end
end

if ~exist('allOn','var') || ~exist('allOff','var')
   allOn  = projValue*ones(height,width,'uint8');
   allOff = zeros(height,width,'uint8');
end


%Clear any existing images
if 7 == exist('Image', 'dir')
    rmdir('Image', 's')
end

%Remake the directory
mkdir('Image');

cd Image

imwrite(allOn, 'GrayCode01.jpg');
imwrite(allOff, 'GrayCode02.jpg');

i = 1;
j = 1;
k = 1;
for j = 1:size(I,1)
   for i = 1:size(I,2)
       fname = sprintf('GrayCode0%d.jpg', (k + 2));
       imwrite(I{j,i}, fname);
       k = k + 1;
       fname = sprintf('GrayCode0%d.jpg', (k + 2));
       imwrite(J{j,i}, fname);
       k = k + 1;
   end
end
