from bunch import Bunch
import socket
from datetime import datetime

_today = str(datetime.today())
_date, _na = _today.split()

cfg = Bunch(
    # backup_vol='/mnt/backups',
    backup_vol='/var/tmp',
    backup_dir="{}_{}".format( socket.gethostname(), _date ),
    sysdisk='/dev/sda',
    vol_group='saucyvg',
    debug=True,
)
