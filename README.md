# Extract_patches_and_masks_from_Whole_Slide_Images

This code creates masks from polygon annotations on a Whole Slide Images and extracts corresponding image patches. The annotation coordinates have to be provided in XML file format.




### Workflow:


#### 1. Load your Whole Slide Image in ASAP.
   
   Download a sample whole-slide image here:
   
   https://data.kitware.com/api/v1/file/5899dd6d8d777f07219fcb23/download
   
   Download ASAP here:
   
   https://github.com/computationalpathologygroup/ASAP/releases
  
  
#### 2. Draw a rectangl which will be Region Of Interest.
   
   IMPORTANT: Only draw a single ROI. If you want to annotate several ROI within the same WSI you should save each ROI in a
              separate xml file.
              
#### 3. Draw annotations inside this rectangle using the polygon annotation tool

![](Images/annoation_of_ROI_in_ASAP.png)


#### 4. Export the annotations as xml file.

   IMPORTANT: The xml file should have the following name:
              xml-filename = WSI-filename_ROI_something.xml 
              
              Example:
              
                 WSI-filename: 02.11715_1E_HE.mrxs
                 
                 xml-filename: 02.11715_1E_HE_ROI_1.xml


#### 5. Created masks and corresponding images patches
```python

from prepare_data import PrepareData
import matplotlib.pyplot as plt 
path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"
target_path = "/path/where/images/and/masks/should/be/saved"
image_minimum_width = 300
image_minimum_height = 300

data = PrepareData(path_to_WSI_folder, path_to_xml_folder,  image_minimum_width, image_minimum_height,  save=True, separate_objects=False target_path=target_path)

PrepareData.create_images_and_masks_for_all_files(data)
  
  
```
##### 5.1) Cut the saved image to the desired size
```
from prepare_data import PrepareData
import matplotlib.pyplot as plt 
path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"
target_path = "/path/where/images/and/masks/should/be/saved"
image_minimum_width = 300
image_minimum_height = 300
desired_width = 300
desired_height = 300

data = PrepareData(path_to_WSI_folder, path_to_xml_folder,  image_minimum_width, image_minimum_height,  save=True, separate_objects=False target_path=target_path)
PrepareData.create_images_and_masks_for_all_files(data)
data.cut_images(desired_width, desired_height)
```


##### 5.2 In case you want to save each annotated object in a separate mask set the option  separate_objects=True
```
from prepare_data import PrepareData
import matplotlib.pyplot as plt 
path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"
target_path = "/path/where/images/and/masks/should/be/saved"
image_minimum_width = 300
image_minimum_height = 300

data = PrepareData(path_to_WSI_folder, path_to_xml_folder,  image_minimum_width, image_minimum_height,  save=True, separate_objects=True target_path=target_path)
PrepareData.create_images_and_masks_for_all_files(data)
```








