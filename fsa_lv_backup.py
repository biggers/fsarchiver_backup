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

    vg = lvm.get_vg(cfg.vol_group, "w")
    size = lv.size(units='MiB')

    # lv_snap = vg.create_lv(snaplv, size, "MiB")
    lv_snap_name = "{}_{}".format(lv.name, snaplv)
    lvcreate(lv_path, s=True, n=lv_snap_name, L=size, _out=sys.stderr)

    lv_backup = os.path.join(cfg.backup_path, lv.name + '.fsa')
    lv_snap = os.path.join('/dev', cfg.vol_group, lv_snap_name)

    fsarchiver("-d", "-o", "savefs", lv_backup, lv_snap, _out=sys.stderr)

    # clean up....
    lvremove(f=lv_snap, _out=sys.stderr)


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
        if cfg.debug and lv.name != 'vagrantlv':
            continue
        else:
            backup_one_lv(cfg, lvm, lv)

if __name__ == '__main__':
    main()
