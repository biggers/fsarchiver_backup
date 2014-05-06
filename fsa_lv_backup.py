from __future__ import print_function

import os
import sys
import shutil

from sh import sudo, mount
from sh import sfdisk, fsarchiver
from sh import lvcreate, lvremove, vgcfgbackup, pvdisplay
from sh import echo

# import logging

def metadata_backup(cfg):
    """ Backup the LVM, disk metadata, for this system
    """
    # log the actions
    # stderr of commands to "log"

    na, dev, device = cfg.sysdisk.split('/')

    sfd_file = os.path.join(cfg.backup_path, device + '.sfd')
    sfdisk(d=cfg.sysdisk, _out=sfd_file)

    sfd_file_long = os.path.join(cfg.backup_path, device + '.sfd_long')
    sfdisk(l=cfg.sysdisk, _out=sfd_file_long)

    vgcfg = os.path.join(cfg.backup_path, 'lvm.conf')
    vgcfgbackup( f=vgcfg )

    shutil.copy('/etc/fstab', cfg.backup_path)   # backup 'fstab'


def backup_one_lv(cfg, lvm, lv, snaplv='snap_lv'):
    """ backup one LV, to {backup_path}/{lv}.fsa
    """
    lv_path = os.path.join('/dev', cfg.vol_group, lv.name)
    lv_snap = os.path.join('/dev', cfg.vol_group, snaplv)

    vg = lvm.get_vg(cfg.vol_group, "w")
    size = lv.size(units='MiB')

    # lvcreate -l 10%VG -s -n 20140412_lvol1 /dev/vg0/lvol1
    # The above example creates a snapshot logical volume called
    # 20140412_lvol1, based on the logical volume lvol1 in volume group
    # vg0. It uses 10% of the space (extents actually) allocated to the
    # volume group.

    # lv_snap = vg.create_lv(snaplv, size, "MiB")
    snapname = "{}_{}".format(lv.name, snaplv)
    echo(lv_path, s=True, n=snapname, L=size, _out=sys.stderr)  # lvcreate

    lv_backup = os.path.join(cfg.backup_path, lv.name + '.fsa')
    echo(lv_backup, lv_snap, o='savefs', _out=sys.stderr) # fsarchiver

    echo(f=lv_snap, _out=sys.stderr) # lvremove


def all_lvs(cfg):
    """
    """
    from lvm2py import LVM

    lvm = LVM()
    vg = lvm.get_vg(cfg.vol_group)
    lvs = vg.lvscan()

    return lvs, lvm


def main():
    from config import cfg
    import errno
    from pprint import pprint

    pprint(cfg)

    cfg.backup_path = os.path.join(cfg.backup_vol, cfg.backup_dir)
    try:
        os.mkdir(cfg.backup_path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print(e)
        else:
            raise

    metadata_backup(cfg)

    log_vols, lvm = all_lvs(cfg)
    for i, lv in enumerate(log_vols):
        if cfg.debug and i > 2:
            break
        backup_one_lv(cfg, lvm, lv)

if __name__ == '__main__':
    main()
