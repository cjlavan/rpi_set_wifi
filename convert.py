import os
import sys
import subprocess
from unipath import Path

def convert(OUTPUT_DIR):
    filenames = []
    for filename in os.listdir(OUTPUT_DIR): 
	if filename.endswith('.m4a'):
	    filenames.append(filename)

    for filename in filenames:
        subprocess.call([
            "avconv", "-y", "-i",
            os.path.join(OUTPUT_DIR, filename),
	    "-b", "128k",
            os.path.join(OUTPUT_DIR, '%s.mp3' % filename[:-4])
            ])
    remove_files(OUTPUT_DIR)
	
def remove_files(OUTPUT_DIR):
	onlyfiles = [ 
        filename 
        for filename in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, filename)) 
        ]

	for filename in onlyfiles:
		if (filename.lower().endswith('.m4a')):
			os.remove(os.path.join(OUTPUT_DIR, filename))
