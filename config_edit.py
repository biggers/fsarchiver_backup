from bunch import Bunch
import socket
from datetime import datetime

_today = str(datetime.today())
_date, _na = _today.split()

cfg = Bunch(
    backup_vol='/mnt/backups',
    sysdisk='/dev/sda',

    # NOT working, yet! Leave empty!
    lvs_to_backup=(),

    lnx_partitions={'/boot':'/dev/sda1'},
    vol_group='saucyvg',

    backup_dir="{}_{}".format( socket.gethostname(), _date ),
    debug=False,
)
