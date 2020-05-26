
from prepare_data_functions import xml_to_coordinates, calc_number_of_iterations_for_sliding_window, assign_corresponding_files, adapt_sliding_window_size_for_ROI, create_training_images, create_masks
from PIL import Image
import numpy as np

#from read_xml import xml_to_coordinates

import os
import re



class PrepareData:
    def __init__(self, path_to_WSI_folder, path_to_xml_folder, patch_min_width, patch_min_height, save=False, separate_objects=False, target_path=None):
        self.patch_min_width = patch_min_width
        self.patch_min_height = patch_min_height
        self.path_to_WSI_folder = path_to_WSI_folder
        self.path_to_xml_folder = path_to_xml_folder
        self.WSI_file_names = sorted([f for f in os.listdir(path_to_WSI_folder) if re.match(r'.*mrxs', f)])
        self.xml_file_names = sorted([f for f in os.listdir(path_to_xml_folder) if re.match(r'.*xml$', f)])
        self.save = save
        self.separate_objects = separate_objects
        self.target_path = target_path


    def create_images_and_masks_for_all_files(self):
        # creates images and mask for all WSI and annotation inside a folder
        # TODO maybe implement somthing that you can run that for a specific WSI and annotation file (in case the folder is full of other WSI and annotation files)
        all_images = []
        all_masks = []
        # Dictionary of WSI file names (key) and list of xml file names
        WSI_and_xml_files = assign_corresponding_files(self.path_to_WSI_folder, self.path_to_xml_folder)

        # key =  WSI file (name, path ???)
        for key in WSI_and_xml_files:
            WSI_path = key
            # list of xml files paths corresponding to a WSI file name
            lst_of_corresponding_xml_files = WSI_and_xml_files[key]

            # iterate over the xml file name belonging to one WSI
            for ROI_annoations_path in lst_of_corresponding_xml_files:
                # get xml coordinates from a single xml file (annotations of a single ROI)
                xml_coordinates = xml_to_coordinates(ROI_annoations_path)

                x, y = calc_number_of_iterations_for_sliding_window(self.patch_min_width, self.patch_min_height, WSI_path, ROI_annoations_path)
                print("number of iterations:", x,y)
                adapted_patch_width, adapted_patch_height = adapt_sliding_window_size_for_ROI(self.patch_min_width, self.patch_min_height, WSI_path, ROI_annoations_path )
                print(adapted_patch_height)
                print(adapted_patch_width)

                # images: Dictionary of image names and images, for one ROI
                images = create_training_images(adapted_patch_width, adapted_patch_height, WSI_path, ROI_annoations_path, self.save, self.separate_objects, self.target_path)

                # masks: Dictionary of mask names and masks, for one ROI
                masks = create_masks(adapted_patch_width, adapted_patch_height, WSI_path, ROI_annoations_path, self.save, self.separate_objects, self.target_path)


                all_images.append(images)
                all_masks.append(masks)

        return all_images, all_masks

# TODO: Finish implementing this function, which should take a single WSI and xml file as input
    def creat_images_and_masks(self):
        x, y = calc_number_of_iterations_for_sliding_window(self.patch_min_width, self.patch_min_height, WSI_path,
                                                            ROI_annoations_path)
        print("number of iterations:", x, y)
        adapted_patch_width, adapted_patch_height = adapt_sliding_window_size_for_ROI(self.patch_min_width,
                                                                                      self.patch_min_height, WSI_path,
                                                                                      ROI_annoations_path)
        print(adapted_patch_height)
        print(adapted_patch_width)

        # images: Dictionary of image names and images, for one ROI
        images = create_training_images(adapted_patch_width, adapted_patch_height, WSI_path, ROI_annoations_path,
                                        self.save, self.separate_objects, self.target_path)

        # masks: Dictionary of mask names and masks, for one ROI
        masks = create_masks(adapted_patch_width, adapted_patch_height, WSI_path, ROI_annoations_path, self.save,
                             self.separate_objects, self.target_path)

        all_images.append(images)
        all_masks.append(masks)


#TODO: This funtion should also work when only the target path is specifiyed and the other class arguments are empthy

    def cut_images(self, desired_width=None, desired_height=None):
        # If images and masks are already in a separate folder dont forget to apply this function in both folders !!!

        file_names = [f for f in os.listdir(self.target_path) if re.match(r'.*png$', f)]
        file_names = sorted(file_names)

        for file_name in file_names:
            img_path = os.path.join(self.target_path, file_name)
            img = Image.open(img_path)
            img = np.array(img)
            # print(np.shape(img))
            # plt.imshow(img)
            # plt.show()

            img = np.array(img)
            width = np.shape(img)[1]
            height = np.shape(img)[0]

            difference_in_width = width - desired_width
            difference_in_height = height - desired_height

            x_1 = int(difference_in_width / 2)
            x_2 = int(width - difference_in_width / 2)

            y_1 = int(difference_in_height / 2)
            y_2 = int(height - difference_in_height / 2)

            img = img[y_1:y_2, x_1:x_2:]

            img = Image.fromarray(img)
            new_file_path = os.path.join(self.target_path, file_name)
            img.save(new_file_path)


