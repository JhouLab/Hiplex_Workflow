import os
from ij import IJ, ImagePlus, WindowManager
from ij.io import DirectoryChooser, FileSaver
from ij.gui import GenericDialog
from ij.plugin import ZProjector, ChannelSplitter, Concatenator
from loci.plugins import BF
from loci.formats import ImageReader
from loci.formats import MetadataTools
from loci.plugins.in import ImporterOptions

def crop(inDir):
	minH = -1
	minW = -1
	#search tree from given directory for smallest image
	for root, directories, filenames in os.walk(inDir):
		for filename in filenames:
  			if filename.endswith(".tiff"):
  				  imp = IJ.openImage(os.path.join(inDir, filename))
  				  h = imp.getHeight()
  				  w = imp.getWidth()
  				  if minH == -1:
  				  	minH = h
  				  elif h < minH:
  				  	minH = h
  				  if minW == -1:
  				  	minW = w
  				  elif w < minW:
  				  	minW = w
  	print "min hight: ", minH
  	print "min width: ", minW
  	#loop through directory tree again, loading each image and cropping from center
  	for root, directories, filenames in os.walk(inDir):
		for filename in filenames:
  			if filename.endswith(".tiff"):
  				  imp = BF.openImagePlus(os.path.join(inDir, filename))
  				  imp = imp[0]
  				  ip = imp.getProcessor().resize(minW, minH)
  				  name = imp.getTitle()
  				  fname = str(name) + "_cropped.tiff"
  				  imp2 = ImagePlus("cropped", ip)
  				  fs = FileSaver(imp2)
  				  fs.saveAsTiff(inDir+"/"+fname)

def stitch(indir):
	IJ.run("Grid/Collection stitching", 
	   "type=[Unknown position] " + 
	   "order=[All files in directory] " +
	   "directory=" + inDir + " " + 
	   "output_textfile_name=TileConfiguration.txt " + 
	   "fusion_method=[Linear Blending] " + 
	   "regression_threshold=0.30 " +
	   "max/avg_displacement_threshold=2.50 " + 
	   "absolute_displacement_threshold=3.50 " + 
	   "frame=1 " + 
	   "subpixel_accuracy " + 
	   "display_fusion " + 
	   "computation_parameters=[Save computation time (but use more RAM)] " +
	   "image_output=[Write to disk] " +
	   "output_directory=" + inDir);

def register(inDir):
	#load images and add to stack
	for root, directories, filenames in os.walk(inDir):
		imps = -1
		for filename in filenames:
			if filename.endswith(".tiff"):
  				  imp = IJ.openImage(os.path.join(inDir, filename))
  				  if imps == -1:
  				  	imps = imp
  				  else:
  				  	imps = Concatenator.run(imps, imp)
  		if (imps != -1):
  			#Register
  			IJ.run(imps, "Linear Stack Alignment with SIFT MultiChannel", "registration_channel=1 initial_gaussian_blur=1.60 steps_per_scale_octave=3 minimum_image_size=64 maximum_image_size=1024 feature_descriptor_size=4 feature_descriptor_orientation_bins=8 closest/next_closest_ratio=0.92 maximal_alignment_error=25 inlier_ratio=0.05 expected_transformation=Rigid interpolate")
			outDir = os.path.join(str(inDir), "reg", "")
			print outDir
			if os.path.exists(outDir) == False:
				os.mkdir(outDir)
			#get current image
			aligned = WindowManager.getImage("Aligned_Untitled")
			#save registered stack
			fs = FileSaver(aligned)
			fs.saveAsTiff(outDir + "/" +"Reg_Stack.tif")
			#Export to RGB tifs with channels separated and partially pseudo-colored
			#Need to expand pseudo-coloring to include 16 different colors
			IJ.run("HiPlex ConvertForPhotoshop Part2", "specify=" + outDir);
		
def createMIP(stack):
	mip = ZProjector(stack)
	mip.setMethod(ZProjector.MAX_METHOD)
	mip.setStopSlice(stack.getNSlices())
	mip.doHyperStackProjection(False)
	return mip.getProjection()

def export(workFile, outDir, inInclude, inExclude, inMaxBool):
	reader = ImageReader()
	omeMeta = MetadataTools.createOMEXMLMetadata()
	reader.setMetadataStore(omeMeta)
  	reader.setId(workFile)
  	cnt = reader.getSeriesCount()
  	for f in range(cnt):
  		options = ImporterOptions()
  		options.setId(workFile)
  		options.setSeriesOn(f, True)
  		name = omeMeta.getImageName(f)
  		if (inInclude in name) or (inInclude == "<NONE>"):
  			if (inExclude not in name) or (inExclude == "<NONE"):
  				print "processing: ", name
  				imps = BF.openImagePlus(options)
  				if (inMaxBool == True):
  					imp = createMIP(imps[0])
  				else:
  					imp = imps[0]
  				fs = FileSaver(imp)
  				fname = name + ".tiff"
  				fs.saveAsTiff(outDir+"/"+fname)
  	reader.close()

def run():
	#build GUI and get responses
	IJ.log("File_Processing.py started")
	gui = GenericDialog("Processing Options")
	gui.addCheckbox("Export Images", True)
	gui.addStringField("Filetype of images to import: ", ".lif")
	gui.addStringField("Include files containing string: ", "<NONE>")
	gui.addStringField("Ignore files containing string in name (overrides above): ", "<NONE>")
	gui.addChoice("Choose how exported images should be stored", ["One folder", "Separate folders (image title)", "Concatenate (slide number)"], "One folder")
	gui.addCheckbox("Export as max projections", True)
	gui.addCheckbox("Stitch exported images and create separate folder", False)
	gui.addCheckbox("Crop all exported images to smallest", True)
	gui.addCheckbox("register all exported images", True)
	gui.showDialog()
	if gui.wasOKed():
		inExport = gui.getNextBoolean()
		inFileType = gui.getNextString()
		inInclude = gui.getNextString()
		inExclude = gui.getNextString()
		inStoreInt = gui.getNextChoiceIndex()
		inMaxBool = gui.getNextBoolean()
		inStitchBool = gui.getNextBoolean()
		inCropBool = gui.getNextBoolean()
		inRegBool = gui.getNextBoolean()
	else:
		IJ.log("Script Cancelled")
		return
	#get input directory
	inDir = DirectoryChooser("Input directory").getDirectory()
	if (inDir == None):
		IJ.log("Error: No input directory selected, ending script")
		return
	outDir = "Default"
	
  	#loop through root directory and convert all files of given filetype
  	if inExport == True:
  		for root, directories, filenames in os.walk(inDir):
  			for filename in filenames:
  				if filename.endswith(inFileType):
  					IJ.log("Exporting " + filename)
  					#get working directory
  					workFile = os.path.join(root, filename)
  					#select and create one folder in selected (in) directory
  					if inStoreInt == 0:
  						dirName = "processed_images"
  						outDir = os.path.join(inDir, dirName)
  						if os.path.exists(outDir) == False:
  							os.mkdir(outDir)
  			  		#make directory for each image file name
  					if inStoreInt == 1:
  						dirName = filename + "_processed"
  						outDir = os.path.join(inDir, dirName)
  						if os.path.exists(outDir) == False:
  							os.mkdir(outDir)
  					#concatenate files based on slide number
  					#expects slide number as second segment of file name separated by underscores (i.e R1_Slide1B-1_Merged)
  					if inStoreInt == 2:
  						split = filename.split("_")
  						dirName = split[1]
  						outDir = os.path.join(inDir, dirName)
  						if os.path.exists(outDir) == False:
  							os.mkdir(outDir)
  					export(workFile, outDir, inInclude, inExclude, inMaxBool)
  					
  				
  	if inStoreInt == 0 and inExport == True:
  		outDir = os.path.join(inDir, "processed_images")
		if inStitchBool == True:
			stitch(outDir)
  		if inCropBool == True:
  			crop(outDir)
  		if inRegBool == True:
  			register(outDir)
  	else:
  		for root, directories, filenames in os.walk(inDir):
  			for directory in directories:
  				IJ.log("Processing " + directory)
  				outDir = os.path.join(root, directory)
  				if inStitchBool == True:
  					stitch(outDir)
  				if inCropBool == True:
  					crop(outDir)
  				if inRegBool == True:
  					register(outDir)
  					
  	
  	IJ.log("Script Finished")
  				
run()  		