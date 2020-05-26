# Extract_patches_and_masks_from_Whole_Slide_Images

This code creates masks from polygon annotations on a Whole Slide Images and extracts corresponding image patches.
The annotation coordinates have to be provided in XML file format.




### Workflow:

### 1. Download a sample whole-slide image:
   https://data.kitware.com/api/v1/file/5899dd6d8d777f07219fcb23/download


2. Load your Whole Slide Image in ASAP.
   Download ASAP here:
   https://github.com/computationalpathologygroup/ASAP/releases
  
  
3. Draw a rectangle which will be your Region Of Interest (ROI). 
   IMPORTANT: Only draw ONE ROI. If you want to annotate several ROI within the same WSI you should save each ROI in a
              separate xml file.
              
4. Draw Annotations inside this Rectangle using the Polygon tool


5. Export the Annotations as xml file.
   IMPORTANT: The xml file should have the following name:
              xml-filename = WSI-filename_ROI_something.xml (somthing can be replaced with anything you want)
              
              
              
```python

  from prepare_data import PrepareData
  import matplotlib.pyplot as plt 

   data = PrepareData(path_to_WSI_folder, path_to_xml_folder, image_minimum_width, image_minimum_height, save=False,
   target_path=None)
   

```






