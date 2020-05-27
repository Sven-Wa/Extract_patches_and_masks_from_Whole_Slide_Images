# Extract patches and masks from Whole Slide Images 

This code creates masks from polygon annotations on a Whole Slide Images and extracts corresponding image patches. The annotation coordinates have to be provided in XML file format.




### Workflow:


#### 1. Load your Whole Slide Image in ASAP.
   Download a sample whole-slide image here: https://data.kitware.com/api/v1/file/5899dd6d8d777f07219fcb23/download
   
   Download ASAP here: https://github.com/computationalpathologygroup/ASAP/releases
  
  
#### 2. Draw a rectangle which will be your Region Of Interest.
   
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


#### 5 Create masks and extract corresponding image patches
The size of the extracted image patches will be adapted to the rectangle size so that all patches together are matching the entire ROI. Therefore you have to specify a minimum image width and height. 5.1 shows you how you can cut the image to a desired size.
```python

from prepare_data import PrepareData
import matplotlib.pyplot as plt 

path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"
target_path= "/path/where/images/and/masks/should/be/saved"
image_minimum_width = 400
image_minimum_height = 400


data = PrepareData(path_to_WSI_folder, 
                   path_to_xml_folder, 
                   image_minimum_width, 
                   image_minimum_height, 
                   save=True, 
                   target_path=target_path)


PrepareData.create_images_and_masks_for_all_files(data)
  
  
```
##### 5.1 Cut the saved images and masks to the desired size
```python
from prepare_data import PrepareData
import matplotlib.pyplot as plt 

path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"

image_minimum_width = 400
image_minimum_height = 400
desired_width = 300
desired_height = 300

target_path="/path/to/the/images/you/want/to/cut"

data = PrepareData(path_to_WSI_folder, 
                   path_to_xml_folder, 
                   image_minimum_width, 
                   image_minimum_height, 
                   save=True, 
                   target_path=target_path)

data.cut_images(desired_width, desired_height)


#cut the masks (change path to the mask folder)
target_path="/path/to/the/masks/you/want/to/cut"

data = PrepareData(path_to_WSI_folder, 
                   path_to_xml_folder, 
                   image_minimum_width, 
                   image_minimum_height, 
                   save=True, 
                   target_path=target_path)

data.cut_images(desired_width, desired_height)

```


##### 5.2 In case you want to save each annotated object in as a separate mask set the option separate_objects=True
```python
path_to_WSI_folder = "/path/to/folder/containing/WSI-files"
path_to_xml_folder = "/path/to/folder/containing/xml-files"
target_path= "/path/where/images/and/masks/should/be/saved"

image_minimum_width = 400
image_minimum_height = 400

data = PrepareData(path_to_WSI_folder, 
                   path_to_xml_folder,  
                   image_minimum_width, 
                   image_minimum_height,  
                   save=True, 
                   separate_objects=True, 
                   target_path=target_path)

PrepareData.create_images_and_masks_for_all_files(data)
```








