# fsa_backup Makefile -- run 'fsarchiver' backup, restores
#
#  (NOTE: must use real Tabs, not spaces, in a Makefile!)

# REFs:  http://docs.python-guide.org/en/latest/dev/virtualenvs/
#        

.PHONY: prelim install run clean

PATH_PFX = bin

all:
	echo "Please edit 'config_edit_me.py', copy to 'config.py'!"

install: prelim virtenv pip

# you have your own Python, so....
install_loc: virtenv pip

prelim:
	sudo aptitude install remake fsarchiver liblvm2app2.2 python-virtualenv

# sh Bunch lvm2py
virtenv:	
	virtualenv --system-site-packages .  # 'lvm2py' reqs liblvm2app2

pip:
	. bin/activate; ${PATH_PFX}/pip install -r requirements.txt

run:
	. bin/activate; ${PATH_PFX}/python fsa_lv_backup.py

clean:
	/bin/true  ## no-opp - now

# "If the .ONESHELL special target appears anywhere in the makefile,
#  then all recipe lines for each target will be provided to a single
#  invocation of the shell..."

# ONESHELL (on Ubuntu) works only for the "fork" of GNU Make, 'remake'!  :-P
# ... Must "quote" shell '$' with another '$', for Make
.ONESHELL:
foo:
	echo $$$$
	a=999
	echo $$$$
	echo $$a
