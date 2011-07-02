#!/usr/bin/python

# License:
# wget -O - https://raw.github.com/avsm/openbsd-xen-sys/master/sys/timetc.h | head -n 8 |  sed 's/Poul-Henning Kamp/GDR!/g' | sed 's/phk@FreeBSD.ORG/gdr@go2.pl/g'

import grp
import os
import os.path
import pwd
from stat import *
import sys

dir = None
user = None
user_printable = "[no user]"
groupids = []
groupnames = []

if len(sys.argv) == 1:
    dir = os.getcwd()
elif len(sys.argv) >= 2:
    if sys.argv[1] in ('-h', '--help'):
        print """
%s [path] [username]

Check is <path> is accessible by <user>
If not, highlight which permissions are conflicting
Path defaults to current working directory
User defaults to current user

By GDR! [http://gdr.geekhood.net/]
""" % sys.argv[0]
        sys.exit(0)
    dir = os.path.abspath(sys.argv[1])

if len(sys.argv) >= 3:
    user_printable = sys.argv[2]
    user = sys.argv[2]
    userid = pwd.getpwnam(user)[2]
else:
    userid = os.stat(dir)[4]
    user = pwd.getpwuid(userid)[0]
    user_printable = user

if user:
    user_printable = user
    groupids.append(pwd.getpwuid(userid)[3])
    groupnames.append(grp.getgrgid(groupids[0])[0])
    for group in grp.getgrall():
        if user in group[3]:
            groupids.append(group[2])
            groupnames.append(group[0])

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[31;40m'
#    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
def warn(text):
    return bcolors.WARNING + text + bcolors.ENDC
def ok(text):
    return bcolors.OKGREEN + text + bcolors.ENDC


def check_if_can_access(stat, path):
    failed = False
    mode = stat[0]
    smode = ''
    # Owner
    if stat[4] == userid:
        if mode & S_IRUSR:
            smode += ok('r')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IRUSR:
            smode += 'r'
        else:
            smode += '-'

    if mode & S_IWUSR:
        smode += 'w'
    else:
        smode += '-'

    if stat[4] == userid and S_ISDIR(mode):
        if mode & S_IXUSR:
            smode += ok('x')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IXUSR:
            smode += 'x'
        else:
            smode += '-'

    smode += " "
    # Group
    if stat[5] in groupids and stat[4] <> userid:
        if mode & S_IRGRP:
            smode += ok('r')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IRGRP:
            smode += 'r'
        else:
            smode += '-'

    if mode & S_IWGRP:
        smode += 'w'
    else:
        smode += '-'

    if stat[5] in groupids and S_ISDIR(mode) and stat[4] <> userid:
        if mode & S_IXGRP:
            smode += ok('x')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IXGRP:
            smode += 'x'
        else:
            smode += '-'

    smode += ' '

    # others
    if stat[5] not in groupids and stat[4] <> userid:
        if mode & S_IROTH:
            smode += ok('r')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IROTH:
            smode += 'r'
        else:
            smode += '-'

    if mode & S_IWOTH:
        smode += 'w'
    else:
        smode += '-'

    if stat[5] not in groupids and stat[4] <> userid and S_ISDIR(mode):
        if mode & S_IXOTH:
            smode += ok('x')
        else:
            smode += warn('-')
            failed = True
    else:
        if mode & S_IXOTH:
            smode += 'x'
        else:
            smode += '-'


    return (smode, failed)


print "Checking access to file/directory %s for user %s" % (dir, user_printable)
if groupids:
    print "User is member of the following groups: %s" % ', '.join(groupnames)

current_dir = dir
u_width = 15
g_width = 10

print " U   G   O \t%s\t%s\tFile" % ('Username'.ljust(u_width), 'Group'.ljust(g_width))
something_failed = False

while True:
    stat = os.stat(current_dir)
    rights, failed = check_if_can_access(stat, current_dir)
    something_failed = something_failed or failed
    print "%s\t%s\t%s\t%s" % (rights, 
                              pwd.getpwuid(stat[4])[0].ljust(u_width),
                              grp.getgrgid(stat[5])[0].ljust(g_width),
                              current_dir,
                             )
    
    if current_dir == '/':
        break
    current_dir = os.path.dirname(current_dir)
