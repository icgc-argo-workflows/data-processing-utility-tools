#!/usr/bin/env python3

"""
 Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: Junjun Zhang <junjun.zhang@oicr.on.ca>
         Linda Xiang <linda.xiang@oicr.on.ca>
 """


import os
import sys
import json
import re
from argparse import ArgumentParser
import hashlib
import subprocess


def get_wf_fullname(wf_short_name):
    wf_fullname = {
        "dna-seq-alignment": "dna-seq-alignment"
    }
    return wf_fullname.get(wf_short_name)

def calculate_size(file_path):
    return os.stat(file_path).st_size

def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()

def run_cmd(cmd):
    p, success = None, True
    try:
        p = subprocess.run([cmd],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
    except Exception as e:
        print('Execution failed: %s' % e)
        success = False

    if p and p.returncode != 0:
        print('\nError occurred, return code: %s. Details: %s' %
              (p.returncode, p.stderr.decode("utf-8")), file=sys.stderr)
        success = False

    if not success:
        sys.exit(p.returncode if p.returncode else 1)

    return

def get_files_info(file_to_upload, filename=None):
    payload_file = {}
    if filename:
        cmd = 'cp %s %s' % (file_to_upload, filename)
        run_cmd(cmd)
        file_to_upload = os.path.realpath(filename)
    payload_file['fileName'] = os.path.basename(file_to_upload)
    payload_file['fileSize'] = calculate_size(file_to_upload)
    payload_file['fileMd5sum'] = calculate_md5(file_to_upload)
    payload_file['fileAccess'] = "controlled"
    payload_file['fileType'] = "BAM"
    payload_file['info'] = {}
    payload_file['info']['data_type'] = "Read Group Unmapped BAM"

    return payload_file

def get_sample_info(sample_list):
    for sample in sample_list:
        for item in ['sampleId', 'specimenId', 'donorId', 'studyId']:
            sample.pop(item, None)
            sample['specimen'].pop(item, None)
            sample['donor'].pop(item, None)

    return sample_list

def main(args):

    with open(args.sequencing_experiment_analysis, 'r') as f:
        metadata = json.load(f)

    read_group = metadata.get("read_group")

    payload = {}
    payload['analysisType'] = {
        "name": "read_group_ubam"
    }

    payload['program_id'] = metadata.get('program_id')
    payload['study'] = metadata.get('program_id')

    payload['sample'] = get_sample_info(metadata.get('sample'))

    payload['inputs'] = []
    payload['inputs'].append({"sequencing_experiment_id": metadata.get('analysisId')})

    #get readgroup info
    for rg in read_group:
        rg_id = rg.get("submitter_read_group_id")
        rg_fname = "".join([c if re.match(r"[a-zA-Z0-9\-_]", c) else "_" for c in rg_id])
        if not args.file_to_upload.startswith(rg_fname): continue
        payload.update(rg)

    #get file info
    payload['file'] = []
    payload['file'].append(get_files_info(args.file_to_upload))

    #get workflow info
    payload['workflow'] = {}
    payload['workflow']['name'] = get_wf_fullname(args.wf_short_name)
    payload['workflow']['short_name'] = args.wf_short_name
    payload['workflow']['version'] = args.wf_version

    payload['experiment'] = {}

    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--sequencing_experiment_analysis", dest="sequencing_experiment_analysis",
                        help="SONG sequencing_experiment_analysis")
    parser.add_argument("-f", "--file_to_upload", dest="file_to_upload", type=str, help="File to upload to server")
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str,
                        help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str,
                        help="workflow version")
    args = parser.parse_args()

    main(args)
