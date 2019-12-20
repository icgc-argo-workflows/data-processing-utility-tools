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


def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_file_info(ubam):
    return {
        'fileName': os.path.basename(ubam),
        'fileSize': calculate_size(ubam),
        'fileMd5sum': calculate_md5(ubam),
        'fileAccess': 'controlled',
        'fileType': 'BAM',
        'info': {
            'data_type': 'Read Group Unmapped BAM'   # dataType may later be supported natively in SONG
        }
    }


def get_sample_info(sample_list):
    for sample in sample_list:
        for item in ['info', 'sampleId', 'specimenId', 'donorId', 'studyId']:
            sample.pop(item, None)
            sample['specimen'].pop(item, None)
            sample['donor'].pop(item, None)

    return sample_list


def get_readgroup_info(ubam, metadata):
    for rg in metadata.get("read_groups"):
        rg_id = rg.get("submitter_read_group_id")
        ubam_name = readgroup_id_to_fname(rg_id)
        if os.path.basename(ubam) == ubam_name:
            return {
                'submitter_read_group_id': rg.pop('submitter_read_group_id'),
                'read_group': rg
            }

    # at this point, not able to find the matching readgroup for the ubam
    sys.exit("Error found: supplied unmapped BAM %s does not match any read group in "
                "supplied sequencing experiment metadata.\n" % ubam)


def readgroup_id_to_fname(rg_id):
    friendly_fname = "".join([ c if re.match(r"[a-zA-Z0-9\.\-_]", c) else "_" for c in rg_id ])
    md5sum = hashlib.md5(rg_id.encode('utf-8')).hexdigest()
    return "%s.%s.lane.bam" % (friendly_fname, md5sum)


def main(args):
    with open(args.sequencing_experiment_analysis, 'r') as f:
        metadata = json.load(f)

    readgroup_info = get_readgroup_info(args.ubam, metadata)

    payload = {
        'analysisType': {
            'name': 'read_group_ubam'
        },
        'study': metadata.get('study'),
        'submitter_read_group_id': readgroup_info['submitter_read_group_id'],
        'read_group': readgroup_info['read_group'],
        'sample': get_sample_info(metadata.get('sample')),
        'file': [ get_file_info(args.ubam) ],
        'experiment': {
            'sequencing_experiment_id': metadata.get('analysisId'),
            'submitter_sequencing_experiment_id': metadata.get('submitter_sequencing_experiment_id')
        },
        'workflow': {
            'name': args.wf_name,
            'short_name': args.wf_short_name if args.wf_short_name else args.wf_name,
            'version': args.wf_version,
            'run_id': args.wf_run,
            'inputs': [
                {
                    'analysis_type': 'sequencing_experiment',
                    'id': metadata.get('analysisId')
                }
            ]
        }
    }

    payload['experiment'].update(metadata.get('experiment', {}))

    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--sequencing_experiment_analysis", dest="sequencing_experiment_analysis",
                        required=True, help="SONG sequencing_experiment_analysis")
    parser.add_argument("-f", "--ubam", dest="ubam", type=str, required=True, help="Unmapped BAM file")
    parser.add_argument("-w", "--wf_name", dest="wf_name", type=str, required=True,
                        help="workflow short name")
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str,
                        help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str, required=True,
                        help="workflow version")
    parser.add_argument("-r", "--wf-run", dest="wf_run", type=str, required=True, help="workflow run ID")
    args = parser.parse_args()

    main(args)
