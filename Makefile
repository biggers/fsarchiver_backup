# fsa_backup Makefile -- run 'fsarchiver' backup, restores
#
#  (NOTE: must use real Tabs, not spaces, in a Makefile!)

# REFs:  http://docs.python-guide.org/en/latest/dev/virtualenvs/
#        

# "If the .ONESHELL special target appears anywhere in the makefile,
#  then all recipe lines for each target will be provided to a single
#  invocation of the shell..."

.ONESHELL:
.PHONY: prelim install run clean

PATH_PFX = bin

prelim:
	sudo aptitude install fsarchiver liblvm2app2.2 python-virtualenv
	virtualenv .

install:
	${PATH_PFX}/pip install sh Bunch lvm2py

run:
	${PATH_PFX}/python fsa_lv_backup.py

clean:
	/bin/true  ## no-opp
