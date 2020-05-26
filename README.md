# Extract_patches_and_masks_from_Whole_Slide_Images

This code creates masks from polygon annotations on a Whole Slide Images and extracts corresponding image patches.
The annotation coordinates have to be provided in XML file format.




### Workflow:


#### 1. Load your Whole Slide Image in ASAP.
   
   Download a sample whole-slide image here:
   
   https://data.kitware.com/api/v1/file/5899dd6d8d777f07219fcb23/download
   
   Download ASAP here:
   
   https://github.com/computationalpathologygroup/ASAP/releases
  
  
#### 2. Draw a rectangle which will be your Region Of Interest (ROI). 
   
   IMPORTANT: Only draw a single ROI. If you want to annotate several ROI within the same WSI you should save each ROI in a
              separate xml file.
              
#### 3. Draw Annotations inside this Rectangle using the Polygon tool

![](Images/annoation_of_ROI_in_ASAP.png)


#### 4. Export the Annotations as xml file.

   IMPORTANT: The xml file should have the following name:
              xml-filename = WSI-filename_ROI_something.xml 
              
              Example:
              
                 WSI-filename: 02.11715_1E_HE.mrxs
                 
                 xml-filename: 02.11715_1E_HE_ROI_1.mrxs



```python

  from prepare_data import PrepareData
  import matplotlib.pyplot as plt 

   data = PrepareData(path_to_WSI_folder, path_to_xml_folder, image_minimum_width, image_minimum_height, save=False,
   target_path=None)
```






