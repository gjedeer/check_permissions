check_permissions.py [path] [username]

Check is _path_ is accessible by _user_. If not, highlight which permissions are conflicting.

* _Path_ defaults to current working directory
* _User_ defaults to current user

---------------------

Users have so many interesting theories about how UNIX permissions work it's hard to 
believe. The number of ways they are making permissions wrong
is somewhere near one bazillion. That's why I needed a simple tool
to make fixing permissions easier. Welcome to 
check_permissions.py

The tool will highlight in red permissions that matter
and should be fixed. 

![screenshot](https://github.com/gjedeer/check_permissions/raw/master/screen.png)
