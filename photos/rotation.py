import os, md5

# A transform is a 3-bit number: 1 = flip x, 2 = flip y, 4 = transpose x-y
# The transpose is done last (e.g. 7 means flip 180 degrees, then transpose).
def swap(x):
    # Swap the bits of a 2-bit number.
    return (x & 1)*2 + (x & 2)/2

def compose(a, b):
    # Compose transform a followed by transform b.
    if a & 4:
        b = (b & 4) + swap(b)
    return a ^ b

def invert(x):
    # Invert a transform.
    if x & 4:
        return (x & 4) + swap(x)
    return x

# The transform that takes EXIF orientation 1 to each EXIF orientation code.
orient_to_transform = [-1, 0,           # row 0 is top, col 0 is left
                           1,           # row 0 is top, col 0 is right
                           3,           # row 0 is bottom, col 0 is right
                           2,           # row 0 is bottom, col 0 is left
                           4,           # row 0 is left, col 0 is top
                           5,           # row 0 is right, col 0 is top
                           7,           # row 0 is right, col 0 is bottom
                           6]           # row 0 is left, col 0 is bottom

transform_to_orient = orient_to_transform.index

def transform(source_orient, target_orient):
    return compose(invert(orient_to_transform[source_orient]),
                   orient_to_transform[target_orient])

def pnmflip_command(x):
    if x:
        command = 'jpegtopnm %s | pnmflip'
        if x & 1: command += ' -lr'
        if x & 2: command += ' -tb'
        if x & 4: command += ' -xy'
        return command + ' | pnmtojpeg > %s'
    return 'cp %s %s'

def jpegtran_command(x):
    return ['cp %s %s',
            'jpegtran -perfect -copy all -flip horizontal %s > %s',
            'jpegtran -perfect -copy all -flip vertical %s > %s',
            'jpegtran -perfect -copy all -rotate 180 %s > %s',
            'jpegtran -perfect -copy all -transpose %s > %s',
            'jpegtran -perfect -copy all -rotate 270 %s > %s',
            'jpegtran -perfect -copy all -rotate 90 %s > %s',
            'jpegtran -perfect -copy all -transverse %s > %s'][x]

def shell_quote(s):
    return "'%s'" % s.replace("'", "'\\''")

def log(message, start=0):
    import time
    t = time.time()
    try:
        stamp = start and '%.2f [%.2f]' % (t, t - start) or '%.2f' % t
        file = open('/tmp/log.txt', 'a')
        file.write('%d - %s: %s\n' % (os.getpid(), stamp, message))
        file.close()
    except:
        pass
    return t

def system(command):
    if 1: start = log(command)
    err = os.system(command)
    if 1: log('status %d' % err, start)
    if err == 0:
        return 1
    if err == 2:
        raise InterruptedError

def get_orient(src):
    pipe = os.popen('jpegexiforient %s' % shell_quote(src))
    return int(pipe.read().strip() or 1)

def set_orient(dst, orient, src=None):
    """Set the EXIF Orientation tag on the file at 'dst'.  If 'src' is given,
    also copy over all other EXIF tags from 'src' to 'dst'."""
    exiftool = 'exiftool -overwrite_original -n'
    if src:
        system('%s -TagsFromFile %s -Orientation=%d %s >/dev/null' %
               (exiftool, shell_quote(src), orient, shell_quote(dst)))
    elif get_orient(dst) != orient:
        system('jpegexiforient -%d %s >/dev/null' % (orient, shell_quote(dst)))
        if get_orient(dst) != orient:
            system('%s -n -Orientation=%d %s >/dev/null' %
                   (exiftool, orient, shell_quote(dst)))
    return get_orient(dst) == orient

class InterruptedError(Exception): pass

def start_work(key):
    path = '/tmp/busy.' + md5.md5(key).hexdigest()
    file = open(path, 'w')
    file.write(str(os.getpid()))
    file.close()
    if 1: log('claim %s' % path)

def finish_work(key):
    path = '/tmp/busy.' + md5.md5(key).hexdigest()
    if os.path.isfile(path):
        pid = int(open(path).read().strip() or 0)
        if pid == os.getpid():
            if 1: log('match %s' % path)
            os.remove(path)
            return 1
    if 1: log('no match %s' % path)

def wait_work(key):
    path = '/tmp/busy.' + md5.md5(key).hexdigest()
    import time
    while os.path.isfile(path):
        time.sleep(0.5)

def rotate_image(src, xform, dst, mode=0666, skip_orient=0):
    if not skip_orient:
        new_xform = compose(orient_to_transform[get_orient(src)], xform)
        new_orient = transform_to_orient(new_xform)
    success = 0
    temp = '/tmp/rotated-%d.jpg' % os.getpid()
    if system(jpegtran_command(xform) % (shell_quote(src), temp)):
        if skip_orient or set_orient(temp, new_orient):
            success = 1
    if not success:
        if system(pnmflip_command(xform) % (shell_quote(src), temp)):
            if skip_orient or set_orient(temp, new_orient, src=src):
                success = 1
    if success:
#        os.rename(temp, dst)   # doesn't work cross-device
        os.system('cp "%s" "%s"' % (temp, dst))
        os.chmod(dst, mode)
        return 1
    if os.path.exists(temp):
        os.remove(temp)

def make_preview(src, size, dst, mode=0666):
    temp = '/tmp/preview-%d.jpg' % os.getpid()
    if system('jpegtopnm %s | ' % shell_quote(src) +
              'pnmscale -xysize %d %d | ' % (size, size) +
              'pnmtojpeg --quality=90 > %s' % temp):
#        os.rename(temp, dst)    # only works if temp and dst are on the same device
        os.system('cp "%s" "%s"' % (temp, dst))
        os.chmod(dst, mode)
        return 1
    if os.path.exists(temp):
        os.remove(temp)
