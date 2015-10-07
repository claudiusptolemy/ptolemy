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

for page in range(270, 332, 2):
    sys.stdout.write('Turn to page %d and press enter when ready.' % page)
    sys.stdin.readline()

    source = sm.OpenSource(source_name)
    source.SetCapability(twain.ICAP_PIXELTYPE, twain.TWTY_UINT16, 0)
    source.SetCapability(twain.ICAP_ORIENTATION, twain.TWTY_UINT16, 1)
    source.SetCapability(twain.ICAP_YRESOLUTION, twain.TWTY_FIX32, 600.0)
    source.SetCapability(twain.ICAP_XRESOLUTION, twain.TWTY_FIX32, 600.0)
    source.RequestAcquire(False,False)
    source.SetXferFileName(filename, twain.TWFF_PNG)
    rv = source.XferImageByFile()
    source.destroy()

    im1 = Image.open(filename)

    box1 = (800, 250, 3400, 4650)
    out1 = os.path.join(cwd, 'india', 'page_%03d.png' % page)
    region = im1.crop(box1)
    region.save(out1)

    box2 = (3900, 250, 6500, 4650)
    out2 = os.path.join(cwd, 'india', 'page_%03d.png' % (page + 1))
    region = im1.crop(box2)
    region.save(out2)


