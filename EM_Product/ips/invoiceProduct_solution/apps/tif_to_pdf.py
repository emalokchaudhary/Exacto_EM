# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 19:32:24 2022

@author: hitesh.singh
"""

from PIL import Image, ImageSequence
import os
import pathlib

def tiff_to_pdf(tiff_path: str,destination_path) -> str:
    pdf_path = tiff_path.replace('.tif', '.pdf')
    try:
        if os.path.exist(pdf_path):
           os.remove(pdf_path)
    except:
        pass
    if not os.path.exists(tiff_path): raise Exception(f'{tiff_path} does not find.')
    image = Image.open(tiff_path)

    images = []
    for i, page in enumerate(ImageSequence.Iterator(image)):
        page = page.convert("RGB")
        images.append(page)
    if len(images) == 1:
        images[0].save(pdf_path)
    else:
        images[0].save(pdf_path, save_all=True,append_images=images[1:])
    return pdf_path
    
            
def bmp2pdf(bmp_folder, save_path, pdf_name, save_png):



    # Import libraries and modules.
    from natsort import os_sorted
    import cv2
    from fpdf import FPDF
    import os
    
    
    
    # Get contents of directory.
    
    p_sep = os.path.sep
    # Creates list for bitmaps and folder name for png files.
    list_bitmaps = []
    bmp_exist = False
    existGDBPath = pathlib.Path(bmp_folder)
    bmp_folder_location = existGDBPath.parent
    #current_direct = os.path.join(bmp_folder_location , p_sep)
    
    # Iterate through folders in directory, finds the bitmap files in each folder, and converts them to png.
    bmp_exist = True
    #img = "{}{}{}".format(bmp_folder, p_sep, n)
    image = cv2.imread(bmp_folder)
    
    image_name = bmp_folder.replace('.bmp', '.png')
    #print("Converting {}".format(image_name))
    
    if not os.path.isfile(image_name):
        cv2.imwrite(image_name, image)
    
    else: 
        pass
        
    list_bitmaps.append(image_name)
    
    # Sorts bitmaps to make sure they go into the pdf in the right order.
    list_bitmaps_s = os_sorted(list_bitmaps)
    pdf_w = FPDF()
    
    # Add the .png images to the PDF.
    for thing in list_bitmaps_s:
        #print("Adding image {}".format(thing))
        pdf_w.add_page()
        pdf_w.image(thing, 0, 0, 210, 297)
        
        if not(pdf_name.endswith(".pdf")):
            file_name_path = os.path.join(bmp_folder_location,pdf_name,".pdf")
        
        else:
            file_name_path = os.path.join(bmp_folder_location,pdf_name)
        
        try:
            if os.path.exist(file_name_path):
               os.remove(file_name_path)
        except:
            pass

        if not os.path.isfile(file_name_path):
            pdf_w.output(file_name_path, "F")
            #print("Finished writing pdf")
        
        else:
            pass
        
        # Delete the temporary png files and folder.
        try:
            os.remove(image_name)
            #print("...png file deleted sucessfully")
        except Exception as e:
            pass
               
    




