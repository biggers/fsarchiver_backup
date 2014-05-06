# fsa_backup Makefile -- run 'fsarchiver' backup, restores
#
#  (NOTE: must use real Tabs, not spaces, in a Makefile!)

# REFs:  http://docs.python-guide.org/en/latest/dev/virtualenvs/
#        

# "If the .ONESHELL special target appears anywhere in the makefile,
#  then all recipe lines for each target will be provided to a single
#  invocation of the shell..."

.PHONY: prelim install run clean

PATH_PFX = bin

all:
	echo "please edit 'config.py', first!"

prelim:
	aptitude install remake fsarchiver liblvm2app2.2 python-virtualenv
	virtualenv --system-site-packages .  # 'lvm2py' reqs liblvm2app2

# sh Bunch lvm2py
install:
	${PATH_PFX}/pip install -r requirements.txt

run:
	${PATH_PFX}/python fsa_lv_backup.py

clean:
	/bin/true  ## no-opp

# ONESHELL only works for the GNU Make "fork", 'remake' 
# ... must "quote" shell '$' with another '$', for Make
.ONESHELL:
foo:
	echo $$$$
	a=999
	echo $$$$
	echo $$a
