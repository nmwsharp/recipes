import os.path, os
from ftplib import FTP, error_perm
import ftplib
from subprocess import call


# Helper to recursively upload
# See https://stackoverflow.com/questions/32481640/how-do-i-upload-full-directory-on-ftp-in-python
def uploadSubDir(ftp, path):

    print("Recursively uploading local directory: " + path)

    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("  Uploading file: " + name + " from " + localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("  Creating directory: " + name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            ftp.cwd(name)
            uploadSubDir(ftp, localpath)           
            ftp.cwd("..")


# Helper to recursively delete everything in the current directory
def deleteRecursiveSubdirs(ftp):

    wd = ftp.pwd()
    print("Recursively deleting directory: " + wd)

    for entry in ftp.mlsd():

        if entry[1]['type'] == 'file':
            print("  Deleting file: " + entry[0])
            ftp.delete(entry[0])
        if entry[1]['type'] == 'dir':
            ftp.cwd(entry[0])
            deleteRecursiveSubdirs(ftp)
            ftp.cwd('..')
            print("  Deleting empty directory: " + entry[0])
            ftp.rmd(entry[0])


### Recompile blog
ret = call(["hugo",  "--theme=hugo_theme_robust_modified"])
if ret != 0:
    print("ERROR: Blog compile failed")
    exit(-1)

### Upload files

ftp = FTP('198.54.115.174')

# Prompt for username and password
uname = input("Website username:")
password = input("Website password:")

ftp.login(uname, password)
ftp.cwd('public_html')

# Delete the old files

# Recursive upload
ftp.cwd('recipes')
deleteRecursiveSubdirs(ftp)
uploadSubDir(ftp, 'public/')

ftp.quit()
print("Done!")
