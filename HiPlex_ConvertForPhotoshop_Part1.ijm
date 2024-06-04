// Run this AFTER you load 4x4 hyperstack, and BEFORE you manually brighten dim channels using Math->Multiply
//
// This sets all channels and slices of hyperstack to have the same 0-65535 display brightness range.
// This is necessary so that manual brightness adjustment will be consistent.
//

Stack.getDimensions(width, height, channels, slices, frames); 

print("Width x Height = " + width + " x " + height);
print("Channels x Slices = " + channels + " x " + slices);

for (i=1;i<=slices;i++) { 
    Stack.setSlice(i);    // This is "Z" = which HiPlex round
	print("Slice: " + i);
	for (j=1; j<=channels; j++) {
		print("  Channel: " + j);
	    Stack.setChannel(j);  // This is "C" = which HiPlex channel
	    setMinAndMax(0, 65535);
		call("ij.ImagePlus.setDefault16bitRange", 16);
	}
}

print("Done");
