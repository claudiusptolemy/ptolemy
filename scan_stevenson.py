import os
import sys

import twain
import Image

cwd = os.getcwd()
filename = os.path.join(cwd, 'image.png')
print os.getcwd()
sm = twain.SourceManager(0)
source_name = sm.GetSourceList()[0]
print 'using source %s' % source_name

for page in range(153,1000):
    sys.stdout.write('Turn to page %d and press enter when ready.' % page)
    sys.stdin.readline()

    source = sm.OpenSource(source_name)
    source.SetCapability(twain.ICAP_PIXELTYPE, twain.TWTY_UINT16, 0)
    source.SetCapability(twain.ICAP_ORIENTATION, twain.TWTY_UINT16, 0)
    source.SetCapability(twain.ICAP_YRESOLUTION, twain.TWTY_FIX32, 600.0)
    source.SetCapability(twain.ICAP_XRESOLUTION, twain.TWTY_FIX32, 600.0)
    source.RequestAcquire(False,False)
    source.SetXferFileName(filename, twain.TWFF_PNG)
    rv = source.XferImageByFile()
    source.destroy()
    os.rename(filename, os.path.join(cwd, 'stevenson', 'page_%03d.png' % page))


