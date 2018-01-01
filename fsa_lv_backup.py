from __future__ import print_function

import os
import sys
from pprint import pprint
import shutil

import sh
from sh import (
    df
    sfdisk,
    fsarchiver,
    pvs,
    lvcreate,
    lvremove,
    vgcfgbackup,
    pvdisplay
)

from lvm2py import LVM


def metadata_backup(cfg):
    """ Back-up the LVM and other disk metadata, for this system
    """
    try:
        na, dev, device = cfg.metadata.split('/')
    except ValueError as e:
        print("{}! cfg.metadata is {}".format(e, cfg.metadata),
              file=sys.stderr)
        return

    sfd_path = os.path.join(cfg.backup_path, device + '.sfd')
    sfdisk(d=cfg.metadata, _out=sfd_path)

    sfd_path_long = os.path.join(cfg.backup_path, device + '.sfd_long')
    sfdisk(l=cfg.metadata, _out=sfd_path_long)

    vgcfg = os.path.join(cfg.backup_path, 'lvm_%s.conf')
    vgcfgbackup(f=vgcfg)

    shutil.copy('/etc/fstab', cfg.backup_path)   # backup 'fstab'

    pvs_out = os.path.join(cfg.backup_path, 'pvs_all.text')
    pvs(o='pv_all', _out=pvs_out)

    df_out = os.path.join(cfg.backup_path, 'df_h.text')
    df(h=True, _out=df_out)


def backup_one_lv(cfg, vg, lv, snaplv='snap_lv'):
    """ Snapshot & back-up one Logical Volume, to {backup_path}/{lv}.fsa
    """
    lv_path = os.path.join('/dev', vg.name, lv.name)
    size = lv.size(units='MiB')
    # lv_snap = vg.create_lv(snaplv, size, "MiB")

    lv_to_backup = None         # /dev/somevg/lv_or_lv_snapshot
    e = None

    try:                        # attempt to backup from a LV snapshot...
        lv_snap_name = "{}_{}".format(lv.name, snaplv)
        lvcreate(lv_path, s=True, n=lv_snap_name, L=size, _out=sys.stderr)
        lv_to_backup = os.path.join('/dev', vg.name, lv_snap_name)

    except sh.ErrorReturnCode_5 as e:
        # Volume group "sysvg00" has insufficient free space (2661
        # extents): 3505 required.
        print("\nWARNING, backing up <{}> LIVE!  No LV snapshot possible...".
              format(lv_path), file=sys.stderr)
        print(e, file=sys.stderr)
        lv_to_backup = lv_path

    fsa_lv_backup = os.path.join(cfg.backup_path, lv.name + '.fsa')
    fsarchiver("-d", "-A", "-o", "savefs", fsa_lv_backup, lv_to_backup,
               _out=sys.stderr)

    # clean up....
    if e is None:
        lvremove(f=lv_to_backup, _out=sys.stderr)


def get_all_lvs(cfg):
    """ Return a List of VolGroup: LogicalVol pairs, to be backed-up
    """
    vgs_to_backup = list()
    vgs = cfg.lvm.vgscan()

    if not cfg.vgs_to_backup:
        return None

    for i, vg in reversed(list(enumerate(vgs))):
        if vg.name not in cfg.vgs_to_backup:
            print("VG {} not in {}".format(vg.name, cfg.vgs_to_backup),
                  file=sys.stderr)
            vgs.pop(i)

    for vg in vgs:
        lvs = vg.lvscan()

        for lv in lvs:
            if lv.name not in cfg.lvs_to_backup:
                print("VG{}: LV {} not in {}".
                      format(vg.name, lv.name, cfg.lvs_to_backup),
                      file=sys.stderr)
                continue

            vgs_to_backup.append((vg, lv))

    return vgs_to_backup


def backup_one_partition(cfg, partition):
    """ Back-up one Linux partition, to {backup_path}/{partition}_part.fsa
    """
    device = cfg.lnx_partitions[partition]

    try:
        na, na, part_name = device.split('/')
    except ValueError as e:
        print("{}! device is {}".format(e, device), file=sys.stderr)
        return

    dev_backup = os.path.join(cfg.backup_path, "{}_part.fsa".format(part_name))

    try:
        fsarchiver("-vv", "-A", "-o", "savefs",
                   dev_backup, device, _out=sys.stderr)
    except sh.ErrorReturnCode_1 as e:
        print(e, file=sys.stderr)


def main():
    from config import cfg
    import errno

    pprint(cfg, stream=sys.stderr)
    pprint("Backup starting @ {}".format(cfg.today), stream=sys.stderr)

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

    for part in cfg.lnx_partitions.keys():
        backup_one_partition(cfg, part)

    vgs_lvs = get_all_lvs(cfg)

    for vg, lv in vgs_lvs:
        backup_one_lv(cfg, vg, lv)


if __name__ == '__main__':
    main()
