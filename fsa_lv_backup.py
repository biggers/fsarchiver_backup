from __future__ import print_function

import os
import sys
import shutil

from sh import sudo, mount, df
from lvm2py import LVM
from sh import sfdisk, fsarchiver
from sh import pvs, lvcreate, lvremove, vgcfgbackup, pvdisplay

def metadata_backup(cfg):
    """ Back-up the LVM and other disk metadata, for this system
    """
    try:
        na, dev, device = cfg.metadata.split('/')
    except ValueError as e:
        print( "{}! cfg.metadata is {}".format(e, cfg.metadata) )
        return

    sfd_path = os.path.join(cfg.backup_path, device + '.sfd')
    sfdisk(d=cfg.metadata, _out=sfd_path)

    sfd_path_long = os.path.join(cfg.backup_path, device + '.sfd_long')
    sfdisk(l=cfg.metadata, _out=sfd_path_long)

    vgcfg = os.path.join(cfg.backup_path, 'lvm_%s.conf')
    vgcfgbackup( f=vgcfg )

    shutil.copy('/etc/fstab', cfg.backup_path)   # backup 'fstab'

    pvs_out = os.path.join(cfg.backup_path, 'pvs_all.text')
    pvs( o='pv_all', _out=pvs_out)

    df_out = os.path.join(cfg.backup_path, 'df_h.text')
    df( h=True, _out=df_out)


def backup_one_lv(cfg, lvm, lv, snaplv='snap_lv'):
    """ Snapshot & back-up one Logical Volume, to {backup_path}/{lv}.fsa
    """
    if cfg.lvs_to_backup:
        if lv.name not in cfg.lvs_to_backup:
            print( "LV {} not in {}".format(lv.name, cfg.lvs_to_backup) )
            return

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
    """ Return a list of Logical Volumes to back-up, and 'lvm' object
    """
    lvm = cfg.lvm
    vg = lvm.get_vg(cfg.vol_group)

    lvs = vg.lvscan()
    return lvs, lvm

def backup_one_partition(cfg, partition):
    """ Back-up one Linux partition, to {backup_path}/{partition}_part.fsa
    """
    device = cfg.lnx_partitions[partition]

    try:
        na, na, part_name = device.split('/')
    except ValueError as e:
        print( "{}! device is {}".format(e, device) )
        return

    dev_backup = os.path.join(cfg.backup_path, "{}_part.fsa".format(part_name))
    fsarchiver("-vv", "-A", "-o", "savefs", dev_backup, device, _out=sys.stderr)

def main():
    from config import cfg
    import errno
    from pprint import pprint

    # "pickle" or write as Py code, the _cfg including:
    #   _cfg.mounts={'/var', '/dev/myvg/var'}'

    pprint(cfg)
    pprint("Backup starting @ {}".format(cfg.today))

    cfg.backup_path = os.path.join(cfg.backup_vol, cfg.backup_dir)
    try:
        os.mkdir(cfg.backup_path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print(e)
        else:
            raise

    cfg.lvm = LVM()
    metadata_backup(cfg)

    log_vols, lvm = all_lvs(cfg)

    for part in cfg.lnx_partitions.keys():
        backup_one_partition(cfg, part)

    for i, lv in enumerate(log_vols):
        backup_one_lv(cfg, lvm, lv)

if __name__ == '__main__':
    main()
