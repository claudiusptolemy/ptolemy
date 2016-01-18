import os
import sys

import twain

if len(sys.argv) != 2:
    print 'usage: scan_map.py filename'
    exit(1)

imagename = sys.argv[1]

cwd = os.getcwd()
filename = os.path.join(cwd, imagename)
print os.getcwd()
sm = twain.SourceManager(0)
source_name = sm.GetSourceList()[0]
print 'scanning from %s to %s' % (source_name, imagename)

source = sm.OpenSource(source_name)
source.SetCapability(twain.ICAP_PIXELTYPE, twain.TWTY_UINT16, 0)
source.SetCapability(twain.ICAP_ORIENTATION, twain.TWTY_UINT16, 1)
source.SetCapability(twain.ICAP_YRESOLUTION, twain.TWTY_FIX32, 600.0)
source.SetCapability(twain.ICAP_XRESOLUTION, twain.TWTY_FIX32, 600.0)
source.RequestAcquire(False, False)
source.SetXferFileName(filename, twain.TWFF_PNG)
rv = source.XferImageByFile()
source.destroy()



