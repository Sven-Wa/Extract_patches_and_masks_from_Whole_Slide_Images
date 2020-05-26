import numpy as np
from PIL import Image
import os
import re
import math
import matplotlib.pyplot as plt
from skimage.draw import polygon
import large_image
import xml.etree.cElementTree as et
import ntpath
from skimage.measure import label
from skimage.color import rgb2gray
import cv2

def xml_to_coordinates(path):
    """
    Take XML annotations from ASAP and return coordinates
    :param path: path of xml file
    :return: coordinates as list of tuples
    """
    xtree = et.parse(path)
    xroot = xtree.getroot()
    xml_coordinates = {}
    for node in xroot:
        for annotation in node:
            name = annotation.attrib.get("Name")
            name+= " "
            name+= annotation.attrib.get("Type")
            for all_coords in annotation:
                tuples_of_coordinates=[]
                for coordinates in all_coords:
                    x = round(float(coordinates.attrib.get("X")))
                    y = round(float(coordinates.attrib.get("Y")))
                    tuples_of_coordinates.append((x,y))
                xml_coordinates[name] = tuples_of_coordinates
    return xml_coordinates


def assign_corresponding_files(path_to_WSI_folder, path_to_xml_folder):
    WSI_file_names = sorted([f for f in os.listdir(path_to_WSI_folder) if re.match(r'.*mrxs', f)])
    xml_file_names = sorted([f for f in os.listdir(path_to_xml_folder) if re.match(r'.*xml$', f)])
    corresponding_files = {}
    for WSI_file_name in WSI_file_names:
        lst = []
        for xml_file_name in xml_file_names:
            # define pattern to replace --> so that only the beginning of the xml file name remains
            pattern = re.compile('(_ROI_[0-9]*.xml)')
            # replace pattern with '' (nothing) inside the file_name
            substring = pattern.sub('', xml_file_name)
            # Check if WSI and xml belong together (each xml file is derived from a certain WSI)
            if substring in WSI_file_name:
                xml_file_path = os.path.join(path_to_xml_folder, xml_file_name)
                WSI_path = os.path.join(path_to_WSI_folder, WSI_file_name)
                lst.append(xml_file_path)
        corresponding_files[WSI_path] = lst
    return corresponding_files

def ROI_coordinates(xml_file_path):
    xml_coordinates = xml_to_coordinates(xml_file_path)
    for key in xml_coordinates:
        if key.endswith('Rectangle'):
            ROI_coordinates = xml_coordinates[key]
    return ROI_coordinates

def annotation_coordinates(xml_file_path):
    xml_coordinates = xml_to_coordinates(xml_file_path)
    # delet Rectangle coordinates
    annotation_coordinates = {key: values for key, values in xml_coordinates.items() if not key.endswith('Rectangle')}
    # delet single point coordinates
    annotation_coordinates = {key: values for key, values in annotation_coordinates.items() if not len(values) <= 1}
    return annotation_coordinates

def ROI_width_and_height_on_WSI(xml_file_path):
    xml_coordinates = xml_to_coordinates(xml_file_path)
    ROI_coords = ROI_coordinates(xml_file_path)
    ROI_width = ROI_coords[1][0] - ROI_coords[0][0]
    ROI_height = ROI_coords[2][1] - ROI_coords[0][1]
    return ROI_width, ROI_height


def ROI_width_and_height_in_python(WSI_path, xml_file_path, magnification=20):
    ROI = load_ROI(WSI_path, xml_file_path, magnification=magnification)
    ROI_width, ROI_height, c = np.shape(ROI)
    return ROI_width, ROI_height


def load_ROI(WSI_path, xml_file_path, magnification=20):
    ROI_width, ROI_height = ROI_width_and_height_on_WSI(xml_file_path)
    ROI_coords = ROI_coordinates(xml_file_path)
    left = ROI_coords[0][0]
    top = ROI_coords[0][1]
    ts = large_image.getTileSource(WSI_path)
    ROI, _ = ts.getRegionAtAnotherScale(
        sourceRegion=dict(left=left, top=top, width=ROI_width, height=ROI_height,
                          units='base_pixels'),
        targetScale=dict(magnification=magnification),
        format=large_image.tilesource.TILE_FORMAT_NUMPY)
    return ROI


def calc_number_of_iterations_for_sliding_window(patch_min_width, patch_min_height, WSI_path, xml_file_path, magnification=20):
    xml_coordinates = xml_to_coordinates(xml_file_path)
    ROI_width, ROI_height = ROI_width_and_height_in_python(WSI_path, xml_file_path, magnification)
    # numbers of times window fits inside ROI
    iterations_x_direction = ROI_width / patch_min_width
    iterations_y_direction = ROI_height / patch_min_height
    return iterations_x_direction, iterations_y_direction


def adapt_sliding_window_size_for_ROI(patch_min_width, patch_min_height, WSI_path, xml_file_path, magnification=20):
    iterations_x_direction, iterations_y_direction = calc_number_of_iterations_for_sliding_window(patch_min_width,
                                                                                                  patch_min_height,
                                                                                                  WSI_path,
                                                                                                  xml_file_path,
                                                                                                  magnification)
    # fraction of window size, necessary to fill the remaining ends of the rectangle
    fraction_in_x_direction = iterations_x_direction % math.floor(iterations_x_direction)
    fraction_in_y_direction = iterations_y_direction % math.floor(iterations_y_direction)

    # fraction multiplied with window size gives us the remaining lengths in x and y direction,
    # necessary to fill the rectangle
    remaining_pixel_in_x_direction = math.floor(fraction_in_x_direction * patch_min_width)
    remaining_pixel_in_y_direction = math.floor(fraction_in_y_direction * patch_min_height)

    # divide remaining pixels by number of windows
    additional_pixel_per_window_in_x_dir = int(remaining_pixel_in_x_direction / math.floor(iterations_x_direction))
    additional_pixel_per_window_in_y_dir = int(remaining_pixel_in_y_direction / math.floor(iterations_y_direction))
    # print("additional_pixel_per_window_in_x_dir",additional_pixel_per_window_in_x_dir)

    # rectangle adapted window size
    adapted_window_width = patch_min_width + additional_pixel_per_window_in_x_dir
    adapted_window_height = patch_min_height + additional_pixel_per_window_in_y_dir

    return adapted_window_width, adapted_window_height


def create_training_images(patch_min_width, patch_min_height, WSI_path, xml_file_path, save=False, separate_objects=False, target_path=None, magnification=20):
    ROI_cords = ROI_coordinates(xml_file_path)

    # top-left coordinates of the ROI
    left = ROI_cords[0][0]
    top = ROI_cords[0][1]
    iterations_x_direction, iterations_y_direction = calc_number_of_iterations_for_sliding_window(patch_min_width,
                                                                                                  patch_min_height,
                                                                                                  WSI_path,
                                                                                                  xml_file_path,
                                                                                                  magnification)

    adapted_patch_width, adapted_patch_height = adapt_sliding_window_size_for_ROI(patch_min_width, patch_min_height,
                                                                                  WSI_path,
                                                                                  xml_file_path, magnification)

    # extract the patient-ID from the xml_file_path
    # https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
    head, tail = ntpath.split(xml_file_path)
    xml_file_name = tail
    pattern = re.compile('(.xml)')
    patient_ID = pattern.sub('', xml_file_name)

    if save == True and separate_objects == False:
        data_path = target_path + "/data"
    if save == True and separate_objects == False and not os.path.exists(data_path):
        os.mkdir(target_path + "/data")


    # move through the image from left to right and from top to bottom,
    # and extract patches form the ROI on the WSI at each step
    training_img = {}
    top -= adapted_patch_height
    number = 0
    for y in range(math.floor(iterations_y_direction)):
        top += adapted_patch_height

        left_2 = left
        left_2 -= adapted_patch_width

        for x in range(math.floor(iterations_x_direction)):
            number += 1
            left_2 += adapted_patch_width

            # extract patches form the ROI on the WSI
            ts = large_image.getTileSource(WSI_path)
            img, _ = ts.getRegionAtAnotherScale(
                sourceRegion=dict(left=left_2, top=top, width=adapted_patch_width, height=adapted_patch_height,
                                  units='base_pixels'),
                targetScale=dict(magnification=magnification),
                format=large_image.tilesource.TILE_FORMAT_NUMPY)

            img_name = patient_ID + "_image_" + str(number)

            training_img[img_name] = img


            if save == True and separate_objects == False:
                img = Image.fromarray(img)
                new_file_path = os.path.join(target_path + "/data/", img_name + '.png')
                img.save(new_file_path)

            ################################################
            if save == True and separate_objects == True:
                new_folder_path = target_path + '/' + patient_ID + "_image_" + str(number)
                if not os.path.exists(new_folder_path):
                    os.mkdir(new_folder_path)
                os.mkdir(new_folder_path + '/image')
                img = Image.fromarray(img)
                new_file_path = os.path.join(new_folder_path + "/image/", img_name + '.png')
                img.save(new_file_path)

            ################################################




    return training_img





def create_masks(patch_min_width, patch_min_height, WSI_path, xml_file_path, save=False, separate_objects=False, target_path=None, magnification=20):
    # Creats masks for one ROI
    # returns dictionary, with mask name and mask
    iterations_x_direction, iterations_y_direction = calc_number_of_iterations_for_sliding_window(patch_min_width,
                                                                                                  patch_min_height,
                                                                                                  WSI_path,
                                                                                                  xml_file_path,
                                                                                                  magnification)

    adapted_patch_width, adapted_patch_height = adapt_sliding_window_size_for_ROI(patch_min_width, patch_min_height,
                                                                                  WSI_path, xml_file_path)

    mask_dict = {}

    head, tail = ntpath.split(xml_file_path)
    xml_file_name = tail
    pattern = re.compile('(.xml)')
    patient_ID = pattern.sub('', xml_file_name)

    start_y = int(-adapted_patch_height)
    end_y = 0
    ROI_mask = create_mask_for_ROI(WSI_path, xml_file_path, magnification)
    number = 0


    if save == True and separate_objects == False:
        gt_path = target_path + "/gt"
    if save == True and separate_objects == False and not os.path.exists(gt_path):
        os.mkdir(target_path + "/gt")





    for row in range(math.floor(iterations_y_direction)):

        # next step
        start_y += int(adapted_patch_height)
        end_y += int(adapted_patch_height)

        start_x = int(-adapted_patch_width)
        end_x = 0

        for col in range(math.floor(iterations_x_direction)):
            number += 1
            start_x += int(adapted_patch_width)
            end_x += int(adapted_patch_width)

            mask = ROI_mask[start_y:end_y, start_x:end_x, :]

            mask_name = patient_ID + "_mask_" + str(number)
            mask_dict[mask_name] = mask


            if save == True and separate_objects == False:
                mask = np.zeros((mask[:, :, :3].shape), dtype=np.uint8)
                mask[:, :, 2] = 1  # set everything to background in blue channel
                mask[:, :, 2][mask[:, :, 1] != 0] = 2  # set glands to 2 in blue channe
                mask = Image.fromarray(mask)
                new_file_path = os.path.join(target_path + "/gt/", mask_name + ".png")
                mask.save(new_file_path)
################################################
            #TODO: if option is set to save==False and separate_objet == True
            #      the mask of each separated object should be saved in a dictionary
            if save == True and separate_objects == True:
                print("********************************************")
                new_folder_path = target_path + '/' + patient_ID + "_image_" + str(number)
                if not os.path.exists(new_folder_path):
                    os.mkidr(new_folder_path)
                print("mask shape: ", mask.shape)
                os.mkdir(new_folder_path + '/mask')
                object = '_object_'
                gray_mask = rgb2gray(np.array(mask))
                print(gray_mask.shape)
                plt.imshow(gray_mask)
                plt.show()
                ret, bw_mask = cv2.threshold(gray_mask, 0, 255, cv2.THRESH_BINARY)
                labels, num = label(bw_mask, return_num=True)
                print(num)
                print(labels.shape)
                plt.imshow(labels)
                plt.show()

                for L in range(1, num + 1):
                    plt.imsave(new_folder_path + '/mask/' + mask_name + object + str(L) + '.png', np.uint8(labels == L))
#######################################################
    return mask_dict





def create_mask_for_ROI(WSI_path, xml_file_path, magnification=20):
    #TODO apply waterhed segmentation to ROI masks so that the objects are properly
    # separated !!!!

    # This function creates a mask for the entire ROI
    # This function is called inside the create mask function

    ROI_coords = ROI_coordinates(xml_file_path)

    left = ROI_coords[0][0]
    top = ROI_coords[0][1]

    # delet ROI-Rectangle coordinate, single point coordinates, so that only annotation coordinates remain
    annotation_coords = annotation_coordinates(xml_file_path)
    masks = {}
    for key in annotation_coords:
        lst = []
        for values in annotation_coords[key]:
            # calculate the corrdinate of masks relative to the upper left corner of target image
            upper_left_corner = tuple([left, top])
            point = tuple(np.subtract(values, upper_left_corner))

            # considering the magnification of the ROI we have to rescale the coordinates
            # point = tuple([int(point[0] * ratio), int(point[1] * ratio)])

            # append new coordinate to the list
            lst.append(point)
        # append a list (one polygon each time) to the dictionary
        masks[key] = lst
    masks

    ROI_width, ROI_height = ROI_width_and_height_in_python(WSI_path, xml_file_path, magnification)
    mask = np.zeros((int(ROI_width), int(ROI_height), 3), dtype=np.uint8)

    # draw masks
    for key in masks:
        rr, cc = polygon(np.array(masks[key])[:, 1], np.array(masks[key])[:, 0], mask.shape)
        mask[rr, cc, 1] = 1

        # encodes the pixelvalues in the blue channel (code from DeepDIVA)

#################################
    # out_mask = np.zeros((mask[:, :, :3].shape), dtype=np.uint8)
    # out_mask[:, :, 2] = 1  # set everything to background in blue channel
    # out_mask[:, :, 2][mask[:, :, 1] != 0] = 2  # set glands to 2 in blue channel
##################################
    return mask



