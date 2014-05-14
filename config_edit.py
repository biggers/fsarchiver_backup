from bunch import Bunch
import socket
from datetime import datetime

_today = str(datetime.today())
_date, _na = _today.split()

cfg = Bunch(
    backup_vol='/mnt/backups',
    metadata='/dev/sda',

    vgs_to_backup=(),
    lvs_to_backup=(),  # this scheme won't work, if LVs not "name-unique" acrossall VolGroups!

    lnx_partitions={'/boot':'/dev/sda1'},
    backup_dir="{}_{}".format( socket.gethostname(), _date ),

    today=_today,
    debug=False,
)

if cfg.debug == True:
    cfg.vgs_to_backup = ('sysvg00',)
    cfg.lvs_to_backup = ('root',)
    cfg.lnx_partitions = {'/boot':'testing.now'}
