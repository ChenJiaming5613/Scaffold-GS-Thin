"""Thin-structure point supplementation, hooked into Scaffold-GS scene loading.

The tools in this folder are standalone scripts with flat imports (``import common``); they are
run in a subprocess so that nothing here leaks into the Scaffold-GS namespace.
"""
import os
import shlex
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
MERGED_NAME = "points3D_merged.ply"


def prepare_init_ply(source_path, images="images", extra_args="", out_dir=""):
    """Return the path of the supplemented initial point cloud, generating it on first use.

    1. ``<out_dir>/points3D_merged.ply`` exists                   -> reuse it
    2. ``sparse/0/points3D.ply.orig`` exists (``--install`` was run) -> ``sparse/0/points3D.ply``
       is already the merged cloud, return None (= keep the default loader path)
    3. otherwise run ``triangulate.py`` once and return the new merged cloud
    """
    out_dir = out_dir or os.path.join(source_path, "thin_init")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(source_path, out_dir)
    merged = os.path.join(out_dir, MERGED_NAME)

    if os.path.exists(merged):
        print(f"[thin_init] found supplemented point cloud: {merged}")
        return merged
    if os.path.exists(os.path.join(source_path, "sparse", "0", "points3D.ply.orig")):
        print("[thin_init] sparse/0/points3D.ply is already the installed merged cloud, using it")
        return None

    cmd = [sys.executable, os.path.join(_HERE, "triangulate.py"),
           "-s", source_path, "--images", images, "--out", out_dir] + shlex.split(extra_args)
    print(f"[thin_init] no supplemented point cloud found, generating it:\n  {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    if not os.path.exists(merged):  # triangulate.py accepted no point
        print(f"[thin_init] WARNING: {merged} was not written, falling back to the COLMAP point cloud")
        return None
    return merged
