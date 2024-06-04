// Run this AFTER you manually brighten dim channels using Math->Multiply
//
// Takes 4x4 hyperstack of aligned HiPlex images, converts to
// 16 separate Photoshop-readable TIF files with 7 unique colors.
// Assumes that first image in each set of 4 is DAPI.

pathToFile = getString("Specify Filepath", "DefaultValue");

print(pathToFile)

run("Hyperstack to Stack");
run("Stack to Images");

// Cache number of images, as it will change once we start processing
n = nImages;
list = getList("image.titles");

// Color cycle
color_num = 0;

for (i=0;i<n;i++) { 
	// Select images by name, not window order, which changes in the course of processing
    selectImage(list[i]);
    run("RGB Color");
    
    // This creates new color image
    run("Make Composite");

	// Choose color:
    if (color_num == 0) {
        Stack.setActiveChannels("001");  // Blue (DAPI)
    } else if (color_num == 1) {
    	Stack.setActiveChannels("010");  // Green
    } else if (color_num == 2) {
    	Stack.setActiveChannels("110");  // Yellow
    } else if (color_num == 3) {
    	Stack.setActiveChannels("100");  // Red
    } else if (color_num == 4) {
	    Stack.setActiveChannels("001");  // Blue (DAPI again)
    } else if (color_num == 5) {
    	Stack.setActiveChannels("011");  // Cyan
    } else if (color_num == 6) {
    	Stack.setActiveChannels("111");  // White
    } else if (color_num == 7) {
    	Stack.setActiveChannels("101");  // Magenta
    }

	// This converts to a format that Photoshop can read
    run("Stack to RGB");

    color_num++;
    if (color_num == 8)
    	color_num = 0;    
    
    title = getTitle; 
    print(title); 
    saveAs("tiff", pathToFile+title); 
    close();  // Close composite image
    selectImage(list[i]);
    close();  // Close original image
}