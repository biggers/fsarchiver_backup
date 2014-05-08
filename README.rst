================================
FSArchiver "bare metal" backups
================================

Scratch
=======
I am "scratching an itch" for a simple, schedulable (``cron``), "bare-metal" backup & restore system, for all my "desktop" Linux systems.  And, I am having a bit of fun with the Python ``sh`` and ``lvm2py`` modules!

Caveats
=======
This project is **still in Development**, but I will attempt to keep ``master`` always in a working state.

I have more Notes coming - here's what I have, for now.  I have tested only on Ubuntu 14.04 LTS.  However, I will create a CentOS 6 *Docker* container, to then  add support and test for RHEL.

Install
========
Go get this project, from Github, and set it up ::

 git clone https://github.com/biggers/fsarchiver_backup.git

 cd fsarchiver_backup

Set-up this project's Python environment, for ``pip`` and required packages.:.  Refer to the ``Makefile`` in this project, for details.::

 sudo make install

 . bin/activate
 make install

Configure
=========
First, review the filesystems and ``LVM`` *logical volumes* on your desktop Linux system.::

NOTE: the *volume group* that you want to use, and what LVs you might want to backup - the default is **all LVs**.::

 sudo vgs  # NOTE: the volume-group to use

 sudo lvs  # NOTE: what LVs you might want to backup (default is all)

 cat /etc/fstab

 df -h     # NOTE: what is the /boot or /root filesystem?

Now, edit ``config_edit.py`` for your backup Storage and other paths, then copy to ``config.py``.::

 vi config_edit.py

 cp -a config_edit.py config.py

Run the backup
==============
It's simple: ::

 sudo make run

You'll get some "feedback" from the LVM commands, at least.  I am working on getting some output from ``fsarchiver``.

References
==========

*Info on doing a bare metal restore using fsarchiver.*  FSarchiver forum entry.  My code is based on this how-to...

 http://www.fsarchiver.org/forums/viewtopic.php?f=16&t=1218


*Backup and bare metal restore your Linux server with SystemRescueCd and fsarchiver*

 http://www.techroot.be/uncategorized/backup-and-bare-metal-restore-your-linux-server-with-systemrescuecd-and-fsarchiver.html
