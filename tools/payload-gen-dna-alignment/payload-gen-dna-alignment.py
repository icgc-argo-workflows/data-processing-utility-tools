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
from argparse import ArgumentParser
import hashlib
import uuid
import subprocess


def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_files_info(file_to_upload):
    return {
        'fileName': os.path.basename(file_to_upload),
        'fileType': file_to_upload.split(".")[-1].upper(),
        'fileSize': calculate_size(file_to_upload),
        'fileMd5sum': calculate_md5(file_to_upload),
        'fileAccess': 'controlled',
        'info': {
            'dataType': 'Aligned Reads' if file_to_upload.split(".")[-1] in ('bam', 'cram') \
                                        else 'Aligned Reads Index'
        }
    }


def get_sample_info(sample_list):
    for sample in sample_list:
        for item in ['info', 'sampleId', 'specimenId', 'donorId', 'studyId']:
            sample.pop(item, None)
            sample['specimen'].pop(item, None)
            sample['donor'].pop(item, None)

    return sample_list


def main(args):
    with open(args.seq_experiment_analysis, 'r') as f:
        seq_experiment_analysis_dict = json.load(f)

    payload = {
        'analysisType': {
            'name': 'dna_alignment'
        },
        'study': seq_experiment_analysis_dict.get('study'),
        'workflow': {
            'name': args.wf_name,
            'short_name': args.wf_short_name if args.wf_short_name else None,
            'version': args.wf_version,
            'run_id': args.wf_run,
            'inputs': [
                {
                    'analysis_type': 'sequencing_experiment',
                    'id': seq_experiment_analysis_dict.get('analysisId')
                }
            ]
        },
        'file': [],
        'sample': get_sample_info(seq_experiment_analysis_dict.get('sample')),
        'experiment': {
            'sequencing_experiment_id': seq_experiment_analysis_dict.get('analysisId'),
            'submitter_sequencing_experiment_id': seq_experiment_analysis_dict.get('submitter_sequencing_experiment_id')
        }
    }

    payload['experiment'].update(seq_experiment_analysis_dict.get('experiment', {}))

    # get inputs from read_group_ubam_analysis
    for ubam_analysis in args.read_group_ubam_analysis:
        with open(ubam_analysis, 'r') as f:
            ubam_analysis_dict = json.load(f)

        payload['workflow']['inputs'].append(
            {
                'analysis_type': 'read_group_ubam',
                'id': ubam_analysis_dict.get('analysisId')
            }
        )

    # get file of the payload
    for f in args.files_to_upload:
      payload['file'].append(get_files_info(f))

    with open("%s.dna_alignment.payload.json" % str(uuid.uuid4()), 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--files_to_upload", dest="files_to_upload", type=str, required=True,
                        nargs="+", help="Aligned reads files to upload")
    parser.add_argument("-a", "--seq_experiment_analysis", dest="seq_experiment_analysis", required=True,
                        help="Input analysis for sequencing experiment", type=str)
    parser.add_argument("-u", "--read_group_ubam_analysis", dest="read_group_ubam_analysis", default=[],
                        help="Input payloads for the analysis", type=str, nargs='+')
    parser.add_argument("-w", "--wf_name", dest="wf_name", required=True, help="Workflow name")
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", help="Workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", required=True, help="Workflow version")
    parser.add_argument("-r", "--wf_run", dest="wf_run", required=True, help="workflow run ID")
    args = parser.parse_args()

    main(args)
