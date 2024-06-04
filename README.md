# Hiplex_Workflow
Fiji Jython Script for processing and registering hiplex images

## Installation
Download the repository and move included files into the Plugins folder of your local Fiji download and restart Fiji (if running).

## Intended Use
This script was developed to process Hiplex rna-scope images for registration and eventual visualization in photoshop. Functions within might be useful for other applications, but might result in bugs.

## Workflow
1. Run Hiplex_Processing_Registration.py and select the desired sections of the workflow to execute. Each should work in series as shown in the menu:
   * Export Images: Select the desired filetype to export to .tif files and select filters to include/exclude images containing a specific string. Exclusionary filters take           priority over inclusionary. Include < NONE > to ignore filters. Additionally, choose one of three folder organization methods for saving the processed files.
     * One Folder: Saves all images in one folder from all files in the given directory
     * Separate Folders: Saves images in separate folders based on their names
     * Concatenate: Saves images in folders based on the title of the image. The script expects image titles to be underscore separated and will look at the second segment of         the image name. For instance, images named R1_Slide1_test.lif and R2_Slide1_test.lif will be saved in the same folder called "Slide1"
    * Export images as max projections if appropriate
    * Stitch images (if processing tilescan images), which will save in a new subfolder based on the above selected folder higherarchy
    * Crop all exported images to the image with the smallest width and height based on the above selected folder higherarchy
    * Register all exported images based on the above selected folder higherarchy

2. Click "OK" and select your working directory. Processed images will also be saved here.
3. For each resulting aligned hyperstack:
   * Run Hiplex_ConvertForPhotoshop_Part1.ijm to scale the image histogram appropriately
   * For each image, use Math>Multiply to adjust the image brightness to the desired levels
   * Run Hipplex_ConvertForPhotoshop_Part2.ijm to convert each image to RGB and psuedocolor each channel. Note every 1st and subsequent 5th channel is colored blue to represent DAPI staining, and the rest are pseudocolored. Also note only the first 8 channels (including DAPI) are colored in a repeating fashion.
