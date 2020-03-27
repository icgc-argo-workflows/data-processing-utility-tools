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

 """

import os
import sys
import re
import json
from argparse import ArgumentParser
import hashlib
import uuid
import subprocess
import copy
from datetime import date
import tarfile


def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_aligned_seq_basename(qc_files):
    # get aligned bam/cram basename from '*.wgs.grch38.(cram|bam).qc_metrics.tgz'
    for f in qc_files:
        m = re.match(r'(.+?\.(cram|bam))\.qc_metrics\.tgz$', f)
        if m: return(m.group(1))

    sys.exit('Error: missing DNA alignment QC metrics file with patten: *.{bam,cram}.qc_metrics.tgz')


def get_rg_id_from_ubam_qc(tar, metadata):
    tar_basename = os.path.basename(tar)  # TEST-PR.DO250122.SA610149.D0RE2_1_.6cae87bf9f05cdfaa4a26f2da625f3b2.lane.bam.ubam_qc_metrics.tgz
    md5sum_from_filename = tar_basename.split('.')[-5]
    if not re.match(r'^[a-f0-9]{32}$', md5sum_from_filename):
        sys.exit('Error: ubam naming not expected %s' % tar_basename)

    for rg in metadata.get("read_groups"):
        rg_id_in_bam = rg.get("read_group_id_in_bam") if rg.get("read_group_id_in_bam") else rg.get("submitter_read_group_id")
        md5sum_from_metadata = hashlib.md5(rg_id_in_bam.encode('utf-8')).hexdigest()
        if md5sum_from_metadata == md5sum_from_filename:
            return rg.get("submitter_read_group_id")

    # up to this point no match found, then something wrong
    sys.exit('Error: unable to match ubam qc metric tar to read group id')


def get_files_info(file_to_upload, seq_experiment_analysis_dict):
    file_info = {
        'fileName': os.path.basename(file_to_upload),
        'fileType': file_to_upload.split(".")[-1].upper(),
        'fileSize': calculate_size(file_to_upload),
        'fileMd5sum': calculate_md5(file_to_upload),
        'fileAccess': 'controlled'
    }

    if re.match(r'.+?\.ubam_qc_metrics\.tgz$', file_to_upload):
        file_info.update({'dataType': 'read_group_qc'})
    elif re.match(r'.+?\.(cram|bam)\.qc_metrics\.tgz$', file_to_upload):
        file_info.update({'dataType': 'alignment_qc'})
    elif re.match(r'.+?\.duplicates_metrics\.tgz$', file_to_upload):
        file_info.update({'dataType': 'alignment_qc'})
    elif re.match(r'.+?\.oxog_metrics\.tgz$', file_to_upload):
        file_info.update({'dataType': 'alignment_qc'})
    else:
        sys.exit('Error: unknown QC metrics file: %s' % file_to_upload)

    extra_info = {}
    tar = tarfile.open(file_to_upload)
    for member in tar.getmembers():
        if member.name.endswith('.extra_info.json'):
            f = tar.extractfile(member)
            extra_info = json.load(f)
            break

    if file_info.get('dataType') == 'read_group_qc':
        map_to_new_id =  {}
        for rg in seq_experiment_analysis_dict['read_groups']:  # build map read_group_id_in_bam to submitter_read_group_id
            if rg.get('read_group_id_in_bam'):
                map_to_new_id[rg['read_group_id_in_bam']] = rg['submitter_read_group_id']
            else:
                map_to_new_id[rg['submitter_read_group_id']] = rg['submitter_read_group_id']

        extra_info['read_group_id'] = map_to_new_id[extra_info['read_group_id']]

    file_info.update({'info': extra_info})

    return file_info


def get_sample_info(sample_list):
    samples = copy.deepcopy(sample_list)
    for sample in samples:
        for item in ['info', 'sampleId', 'specimenId', 'donorId', 'studyId']:
            sample.pop(item, None)
            sample['specimen'].pop(item, None)
            sample['donor'].pop(item, None)

    return samples


def main(args):
    with open(args.seq_experiment_analysis, 'r') as f:
        seq_experiment_analysis_dict = json.load(f)

    payload = {
        'analysisType': {
            'name': 'qc_metrics'
        },
        'studyId': seq_experiment_analysis_dict.get('studyId'),
        'workflow': {
            'name': args.wf_name,
            'version': args.wf_version,
            'run_id': args.wf_run,
            'inputs': [
                {
                    'analysis_type': 'sequencing_experiment',
                    'input_analysis_id': seq_experiment_analysis_dict.get('analysisId')
                }
            ]
        },
        'files': [],
        'experiment': seq_experiment_analysis_dict.get('experiment'),
        'samples': get_sample_info(seq_experiment_analysis_dict.get('samples'))
    }

    new_dir = 'out'
    try:
        os.mkdir(new_dir)
    except FileExistsError:
        pass

    aligned_seq_basename = get_aligned_seq_basename(args.qc_files)

    # get file of the payload
    for f in args.qc_files:
        # renmame duplicates_metrics file to have the same base name as the aligned seq
        if re.match(r'.+\.duplicates_metrics\.tgz$', f):
            new_name = '%s.duplicates_metrics.tgz' % aligned_seq_basename
            dst = os.path.join(os.getcwd(), new_name)
            os.symlink(os.path.abspath(f), dst)
            f = new_name

        # renmame ubam_qc_metrics file to have the same base name as the aligned seq
        if re.match(r'.+?\.lane\.bam\.ubam_qc_metrics\.tgz$', f):
            rg_id = get_rg_id_from_ubam_qc(f, seq_experiment_analysis_dict)
            new_name = '%s.%s.ubam_qc_metrics.tgz' % (re.sub(r'\.aln\.cram$', '', aligned_seq_basename), rg_id)
            dst = os.path.join(os.getcwd(), new_name)
            os.symlink(os.path.abspath(f), dst)
            f = new_name

        payload['files'].append(get_files_info(f, seq_experiment_analysis_dict))

        dst = os.path.join(os.getcwd(), new_dir, f)
        os.symlink(os.path.abspath(f), dst)

    with open("%s.dna_seq_qc.payload.json" % str(uuid.uuid4()), 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-a", "--seq-experiment-analysis", dest="seq_experiment_analysis", required=True,
                        help="Input analysis for sequencing experiment", type=str)
    parser.add_argument("-f", "--qc-files", dest="qc_files", type=str, required=True,
                        nargs="+", help="All QC TGZ files")
    parser.add_argument("-w", "--wf-name", dest="wf_name", required=True, help="Workflow name")
    parser.add_argument("-r", "--wf-run", dest="wf_run", required=True, help="workflow run ID")
    parser.add_argument("-v", "--wf-version", dest="wf_version", required=True, help="Workflow version")
    args = parser.parse_args()

    main(args)
