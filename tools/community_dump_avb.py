#!/usr/bin/env python3

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile


AOSP_TEST_KEYS = {
    "cdbb77177f731920bbe0a0f94f84d9038ae0617d",
    "2597c218aae470a130f61162feaae70afd97f011",
}


def read_metadata(avbtool, path):
    image = avbtool.ImageHandler(str(path), read_only=True)
    footer, header, descriptors, _ = avbtool.Avb()._parse_image(image)
    image.seek(footer.vbmeta_offset if footer else 0)
    blob = image.read(header.SIZE + header.authentication_data_block_size + header.auxiliary_data_block_size)
    offset = header.SIZE + header.authentication_data_block_size + header.public_key_offset
    key = blob[offset:offset + header.public_key_size]
    valid = bool(key) and avbtool.verify_vbmeta_signature(header, blob)
    return valid, key, descriptors, image


def verify_archive(avbtool, source, directory):
    archive = ZipFile(source)
    with archive:
        if len(set(archive.namelist())) != len(archive.infolist()):
            raise ValueError("Duplicate ZIP members")
        if "vbmeta.img" not in archive.namelist():
            return {"status": "no_vbmeta"}
        missing, mismatches, visited = set(), set(), set()

        def extract(name):
            if not re.fullmatch(r"[A-Za-z0-9_]+", name):
                raise ValueError(f"Unexpected partition name: {name!r}")
            filename = name + ".img"
            path = directory / filename
            if path.is_file():
                return path
            try:
                entry = archive.getinfo(filename)
            except KeyError:
                missing.add(name)
                return None
            if entry.file_size > shutil.disk_usage(directory).free:
                raise OSError(f"Insufficient space for {filename}")
            with archive.open(entry) as inp, path.open("xb") as out:
                shutil.copyfileobj(inp, out, 1024 * 1024)
            return path

        def verify(name, expected_key=None):
            path = extract(name)
            if path is None:
                return None
            valid, key, descriptors, image = read_metadata(avbtool, path)
            if not valid or (expected_key is not None and key != expected_key):
                mismatches.add(name)
                return key
            if name in visited:
                return key
            visited.add(name)
            for desc in descriptors:
                if isinstance(desc, avbtool.AvbChainPartitionDescriptor):
                    verify(desc.partition_name, desc.public_key)
                elif isinstance(desc, (avbtool.AvbHashDescriptor, avbtool.AvbHashtreeDescriptor)):
                    partition = desc.partition_name
                    if extract(partition) and not desc.verify(str(directory), ".img", {}, image, False):
                        mismatches.add(partition)
            return key

        root_key = verify("vbmeta")
        if mismatches:
            status = "mismatch"
        elif missing:
            status = "incomplete"
        else:
            status = "consistent"
        result = {"status": status}
        if root_key:
            digest = hashlib.sha1(root_key).hexdigest()
            result["signer"] = "aosp_test" if digest in AOSP_TEST_KEYS else "embedded_key"
        if mismatches:
            result["mismatches"] = sorted(mismatches)
        if missing:
            result["missing"] = sorted(missing)
        return result


def main():
    parser = argparse.ArgumentParser(description="Check AVB consistency in a ZIP of partition images")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--avbtool", required=True, type=Path, help="Path to AOSP avbtool.py")
    parser.add_argument("--work-dir", type=Path, help="Directory for temporary partition images")
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("avbtool", args.avbtool)
    avbtool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(avbtool)
    with TemporaryDirectory(dir=args.work_dir) as work, redirect_stdout(sys.stderr):
        result = verify_archive(avbtool, args.archive, Path(work))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
