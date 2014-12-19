scripts: All my fragmentary scripts
=======

This repo is used to store all kinds of useful scripts (most of them are writed by myself).

All python scripts were developed with python3 (>=3.3), I didn't try it with python2.

####bugzilla
I don't think it's worth using a repo so moving to here.

requirements: click, pymongo, tornado

1. **bugzilla-to-mongo.py:** This is used to fetch data from official bugzilla to my personal mongodb.
    
2. **main_tornado.py:** This is the web service based on the tornado web framework.
    
3. **test-bugzilla.py:** This is a command line tool to test the bugzilla api.
    
4. **tornado-nginx.conf:** This is the configuration file for nginx which is used to proxy the tornado.
    
####fate
This is almost a clone of the bugzilla so I don't list it.
    

**dockerip.sh:** A shell script to get the private ip of a specific container

**enter-docker:** This is copied from https://github.com/jpetazzo/nsenter.git and used to enter into the namespace of a container.

**merge_mail.py:** This is used to merge mail folder based on md5sum but not file name (merge mail of mutt)

**mount-iso.sh:** This is used to mount all iso file of a folder and setup http file server of each mounted point.

**pxemenu-lxml.py:** This is used to parse a http file server page and genreate a pxe menu.

**switch-gw.sh** This is used to switch the default route to another interface.
