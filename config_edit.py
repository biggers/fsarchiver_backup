from attrdict import AttrDict
import socket
from datetime import datetime

_today = str(datetime.today())
_date, _na = _today.split()


cfg = AttrDict(
    backup_vol='/mnt/fsarchiver_backups',
    metadata='/dev/sda',

    vgs_to_backup=(),
    lvs_to_backup=(),

    lnx_partitions={'/boot':'/dev/sda1'},
    backup_dir="{}_{}".format( socket.gethostname(), _date ),

    today=_today,
    debug=False,
)

cfg.vgs_to_backup = ('sysvg00',)
cfg.lvs_to_backup = ('root', 'var', 'local', 'home',)
