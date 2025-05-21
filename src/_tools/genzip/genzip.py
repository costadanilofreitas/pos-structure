import sys
import os
import os.path
import traceback
import zipfile
import platform


print("Python Version", platform.python_version())


# Retrieve the newest (biggest) "last modified" timestamp from the given file list
# returns 0 if a file in the list does not exist
def newest(file_list):
    newest_file = 0
    for file_name in filter(None, file_list):
        if not os.path.exists(file_name):
            if os.path.islink(file_name):
                continue
            return 0
        newest_file = max(newest_file, os.path.getmtime(file_name))
    return newest_file


# Retrieve the oldest (smallest) "last modified" timestamp from the given file list
# returns 0 if a file in the list does not exist
def oldest(file_list):
    oldest_file = 0
    for file_name in filter(None, file_list):
        if not os.path.exists(file_name):
            if os.path.islink(file_name):
                continue
            return 0
        ts = os.path.getmtime(file_name)
        if oldest_file:
            oldest_file = min(oldest_file, ts)
        else:
            oldest_file = ts
    return oldest_file


# Checks if we need to update output files, based on input dates and output dates
def need_update(input_files, output_files):
    input_time = newest(input_files)
    output_time = oldest(output_files)
    if (not output_time) or output_time < input_time:
        return True
    return False


def main(dest, srcdir, arcdir):
    #
    # Iterate over all directories that should be zipped
    #
    if not dest.lower().endswith('.zip'):
        dest += '.zip'
    input_files = []
    for root, dirnames, filenames in os.walk(srcdir):
        for filename in filenames:
            input_files.append(os.path.join(root, filename))
    output_files = [dest]
    # Check if we need to zip this component
    if not need_update(input_files, output_files):
        return 0
    print ("Generating '%s'..." % dest)
    prefixlen = len(srcdir + '/')
    pkg = zipfile.ZipFile(dest, mode="w", compression=zipfile.ZIP_DEFLATED)
    for f in input_files:
        if f.lower().endswith('.css') or f.lower().endswith('.js'):
            pkg.write(f, os.path.join(arcdir, f[prefixlen:]))
        else:
            pkg.write(f, os.path.join(f[prefixlen:]))
    pkg.close()
    return 1


if __name__ == "__main__":
    l = len(sys.argv)
    if l < 3 or l > 4:
        print("Usage:\n    ./genzip.py [destzip] [sourcedir] <[arcdir]>\n")
        sys.exit(255)
    try:
        arcdir = sys.argv[3] if l > 3 else ''
        qty = main(sys.argv[1], sys.argv[2], arcdir)
        if qty == 0:
            print("genzip - up to date!")
        else:
            print("genzip - finished updating %d files" % qty)
    except Exception as _:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
