# fsa_backup Makefile -- run 'fsarchiver' backup, restores
#
#  (NOTE: must use real Tabs, not spaces, in a Makefile!)

# REFs:  http://docs.python-guide.org/en/latest/dev/virtualenvs/
#        

.PHONY: prereqs install run

all:
	echo "Please edit 'config_edit_me.py', copy to 'config.py'!"

install: prereqs virtenv pip

# you have your own Python, so....
install_loc: virtenv pip

prereqs:
	sudo apt-get -y  -u install fsarchiver liblvm2app2.2 python-virtualenv

# 'lvm2py' reqs liblvm2app2
virtenv:	
	virtualenv -p $$(which python2) --system-site-packages ./venv

pip:
	. ./venv/bin/activate; \
	pip install -r requirements.txt

PDB = # "-m pdb"
OPTS = # --metadata-only
# make run  PDB="-m pdb"  OPTS=--metadata-only

# must be run as 'sudo', because of root-restriction 
run:
	. ./venv/bin/activate; \
	sudo --preserve-env ./venv/bin/python2 ${PDB} fsa_lv_backup.py ${OPTS}

clean:
	/bin/rm -rf ./venv
