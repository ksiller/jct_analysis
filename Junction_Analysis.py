# @ File[] (label="Input directory", style="both") inputs
# @ File (label="Output directory", style="directory") outputdir 
# @ String (label="Filter", choices={"Median"}, style="listBox") filter_type
# @ Integer (label="Filter radius", min=1, max=15, value=1) radius
# @ Boolean (label="Save binary mask", default=False, required=False) save_mask
# @ Boolean (label="Show images", default=False, required=False) show_images

import os

from ij import IJ, Prefs, ImagePlus
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.plugin import Duplicator, ZProjector

filters = {"Gaussian Blur": "sigma", "Median": "radius"}

def read_dir(directory, ext):
    files = os.listdir(directory)
    img_files = [os.path.join(directory,f) for f in files if f.split(".")[-1] in ext]
    return img_files

def get_files(inputs, ext=["jpg"]):
    img_files = [read_dir(str(f), ext) if os.path.isdir(str(f)) else [str(f)] for f in inputs]
    flat_filtered = [f for l in img_files for f in l if f.split(".")[-1] in ext]
    exists = [f for f in flat_filtered if os.path.exists(f)]
    return exists

def open_image(imgfile):
	#options = ImporterOptions()
	#options.setId(imgfile)
	#options.setSplitChannels(False)
	#options.setColorMode(ImporterOptions.COLOR_MODE_COMPOSITE)
	#imps = BF.openImagePlus(options)
	#return imps[0]
	imp = IJ.openImage(imgfile)
	return imp

def process(image, filter_type="Median", radius=1, algo="Default"):
    #rm = RoiManager.getRoiManager()
    #rm.reset()
    title = image.getTitle()
    
    mask = image.duplicate()
    
    Prefs.blackBackground = False
    IJ.run(mask, "Convert to Mask", "")
    IJ.run(mask, "Invert", "")
    IJ.run(mask, filter_type+"...", "%s=%d" % (filters[filter_type],radius))
    IJ.run(mask, "Skeletonize", "")
    IJ.run(mask.duplicate(), "Analyze Skeleton (2D/3D)", "prune=none prune_0 calculate show display")
    
    #IJ.run("Set Measurements...", "area mean min centroid integrated display decimal=3")
    #IJ.run(
    #    mask, 
    #    "Analyze Particles...", 
    #    "size="+str(min_area)+"-"+str(max_area) + " add"
    #)
    #rm.runCommand(imp, "Measure")
    mask.setTitle(".".join(title.split(".")[:-1])+"-mask."+title.split(".")[-1])
    return mask

def save_image(img, outputdir, suffix=""):
    filename = ".".join(img.getTitle().split(".")[:-1])+suffix+".tif"
    path = os.path.join(outputdir, filename)
    IJ.saveAsTiff(img, path)
    print "\tSaved mask as", filename
    
# Main code
outputdir = str(outputdir)
if not os.path.isdir(outputdir):
    os.makedirs(outputdir)
	
img_files = get_files(inputs, ext=["jpg"])
if show_images and len(img_files) > 5:
    print "Ignoring show_images flag."
    show_images = False

for item in img_files:
    try:
        img = open_image(item)
        print 'Processing', item
        mask = process(img, filter_type=filter_type, radius=radius)
        if show_images:
            img.show()
            mask.show()
        if save_mask:
            save_image(mask, outputdir)
    except:
        print 'Error, skipping', item
    #rt = ResultsTable.getResultsTable()
    #rt.saveAs(os.path.join(outputdir, "Results.csv"))
print 'Done.\n'
