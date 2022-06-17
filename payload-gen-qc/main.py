#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Copyright (C) 2021,  Ontario Institute for Cancer Research

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Authors:
    Linda Xiang
"""

import os
import sys
import argparse
import subprocess
import json
import re
import hashlib
import uuid
import tarfile
from datetime import date
import copy

workflow_full_name = {
    'pre-alignment-qc': 'Pre Alignment QC Workflow'
}

def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()

def get_rg_id_from_lane_qc(tar, metadata):
    # tar name pattern
    # friendly_rg_id.6cae87bf9f05cdfaa4a26f2da625f3b2.fastqc.tgz
    # friendly_rg_id.6cae87bf9f05cdfaa4a26f2da625f3b2.cutadapt.tgz
    tar_basename = os.path.basename(tar)
    md5sum_from_filename = tar_basename.split('.')[-3]
    if not re.match(r'^[a-f0-9]{32}$', md5sum_from_filename):
        sys.exit('Error: lane naming not expected %s' % tar_basename)

    for rg in metadata.get("read_groups"):
        rg_id = rg.get("submitter_read_group_id")
        friendly_rg_id = "".join([ c if re.match(r"[a-zA-Z0-9\.\-_]", c) else "_" for c in rg_id ])
        md5sum_from_metadata = hashlib.md5(rg_id.encode('utf-8')).hexdigest()
        if md5sum_from_metadata == md5sum_from_filename:
            return friendly_rg_id, rg.get("submitter_read_group_id")

    # up to this point no match found, then something wrong
    sys.exit('Error: unable to match ubam qc metric tar "%s" to read group id' % tar_basename)


def get_files_info(file_to_upload, date_str, analysis_dict):
    file_info = {
        'fileSize': calculate_size(file_to_upload),
        'fileMd5sum': calculate_md5(file_to_upload),
        'fileAccess': 'controlled',
        'info': {
            'data_category': 'Quality Control Metrics',
            'data_subtypes': None,
            'files_in_tgz': []
        }
    }

    submitter_rg_id = None
    process_indicator = None
    if re.match(r'.+?\.fastqc\.tgz$', file_to_upload):
        file_type = 'fastqc'
        file_info.update({'dataType': 'Sequencing QC'})
        file_info['info']['data_subtypes'] = ['Read Group Metrics']
        file_info['info'].update({'analysis_tools': ['FastQC']})
        process_indicator, submitter_rg_id = get_rg_id_from_lane_qc(file_to_upload, analysis_dict)
    elif re.match(r'.+?\.cutadapt\.tgz$', file_to_upload):
        file_type = 'cutadapt'
        file_info.update({'dataType': 'Sequencing QC'})
        file_info['info']['data_subtypes'] = ['Read Group Metrics']
        file_info['info'].update({'analysis_tools': ['Cutadapt']})
        process_indicator, submitter_rg_id = get_rg_id_from_lane_qc(file_to_upload, analysis_dict)
    elif re.match(r'^multiqc\.tgz$', file_to_upload):
        file_type = 'multiqc'
        file_info.update({'dataType': 'Sequencing QC'})
        file_info['info']['data_subtypes'] = ['Read Group Metrics']
        file_info['info'].update({'analysis_tools': ['MultiQC']})
        process_indicator = 'summary'

    else:
        sys.exit('Error: unknown QC metrics file: %s' % file_to_upload)

    # file naming patterns:
    #   pattern:  <argo_study_id>.<argo_donor_id>.<argo_sample_id>.<experiment_strategy>.<date>.<process_indicator>.<file_type>.<file_ext>
    #   process_indicator: pre-alignment(rg_id), alignment(aligner), post-alignment(caller)
    #   example: TEST-PR.DO250183.SA610229.rna-seq.20200319.star.genome_aln.cram
    new_fname = '.'.join([
        analysis_dict['studyId'],
        analysis_dict['samples'][0]['donor']['donorId'],
        analysis_dict['samples'][0]['sampleId'],
        analysis_dict['experiment']['experimental_strategy'].lower() if analysis_dict['experiment'].get('experimental_strategy') else analysis_dict['experiment']['library_strategy'],
        date_str,
        process_indicator,
        file_type,
        'tgz'
      ])    
    
    file_info['fileName'] = new_fname
    file_info['fileType'] = new_fname.split('.')[-1].upper()

    extra_info = {}
    with tarfile.open(file_to_upload, 'r') as tar:
      for member in tar.getmembers():
        if member.name.endswith('qc_metrics.json') or member.name.endswith('.extra_info.json'):
          f = tar.extractfile(member)
          extra_info = json.load(f)
        else:
          if not file_info['info'].get('files_in_tgz'): file_info['info']['files_in_tgz'] = []
          file_info['info']['files_in_tgz'].append(os.path.basename(member.name))

    if file_type =='fastqc':
      for e in extra_info['metrics']:
        e.update({'read_group_id': submitter_rg_id})
    elif file_type == 'cutadapt':
      extra_info['metrics'].update({'read_group_id': submitter_rg_id})
    else:
      pass

    extra_info.pop('tool', None)
    if extra_info:
      file_info['info'].update({'metrics': extra_info.get('metrics', None)})
      file_info['info'].update({'description': extra_info.get('description', None)})

    new_dir = 'out'
    try:
      os.mkdir(new_dir)
    except FileExistsError:
      pass

    dst = os.path.join(os.getcwd(), new_dir, new_fname)
    os.symlink(os.path.abspath(file_to_upload), dst)

    return file_info

def get_basename(metadata):
    study_id = metadata['studyId']
    donor_id = metadata['samples'][0]['donor']['donorId']
    sample_id = metadata['samples'][0]['sampleId']

    if not sample_id or not donor_id or not study_id:
      sys.exit('Error: missing study/donor/sample ID in the provided metadata')

    return ".".join([study_id, donor_id, sample_id])

def get_sample_info(sample_list):
    samples = copy.deepcopy(sample_list)
    for sample in samples:
      for item in ['info', 'sampleId', 'specimenId', 'donorId', 'studyId']:
        sample.pop(item, None)
        sample['specimen'].pop(item, None)
        sample['donor'].pop(item, None)

    return samples

def main():
    """
    Python implementation of tool: payload-gen-qc
    """

    parser = argparse.ArgumentParser(description='Tool: payload-gen-qc')
    parser.add_argument("-a", "--metatada-analysis", dest="metadata_analysis", required=True,
                        help="Input metadata analysis", type=str)
    parser.add_argument("-f", "--files_to_upload", dest="files_to_upload", type=str, required=True,
                        nargs="+", help="All files to upload")
    parser.add_argument("-g", "--genome_annotation", dest="genome_annotation", default="", help="Genome annotation")
    parser.add_argument("-b", "--genome_build", dest="genome_build", default="", help="Genome build")
    parser.add_argument("-w", "--wf-name", dest="wf_name", required=True, help="Workflow name")
    parser.add_argument("-r", "--wf-run", dest="wf_run", required=True, help="workflow run ID")
    parser.add_argument("-s", "--wf-session", dest="wf_session", required=True, help="workflow session ID")
    parser.add_argument("-v", "--wf-version", dest="wf_version", required=True, help="Workflow version")
    args = parser.parse_args()
    
    with open(args.metadata_analysis, 'r') as f:
      analysis_dict = json.load(f)

    payload = {
        'analysisType': {
            'name': 'qc_metrics'
        },
        'studyId': analysis_dict.get('studyId'),
        'info': {},
        'workflow': {
            'workflow_name': workflow_full_name.get(args.wf_name, args.wf_name),
            'workflow_version': args.wf_version,
            'run_id': args.wf_run,
            'session_id': args.wf_session,
            'inputs': [
                {
                    'analysis_type': analysis_dict['analysisType']['name'],
                    'input_analysis_id': analysis_dict.get('analysisId')
                }
            ]
        },
        'files': [],
        'experiment': analysis_dict.get('experiment'),
        'samples': get_sample_info(analysis_dict.get('samples'))
    }
    if args.genome_build:
      payload['workflow']['genome_build'] = args.genome_build
    if args.genome_annotation:
      payload['workflow']['genome_annotation'] = args.genome_annotation

    # pass `info` dict from seq_experiment payload to new payload
    if 'info' in analysis_dict and isinstance(analysis_dict['info'], dict):
      payload['info'] = analysis_dict['info']
    else:
      payload.pop('info')

    if 'library_strategy' in payload['experiment']:
      experimental_strategy = payload['experiment'].pop('library_strategy')
      payload['experiment']['experimental_strategy'] = experimental_strategy

    new_dir = 'out'
    try:
        os.mkdir(new_dir)
    except FileExistsError:
        pass

    # get file of the payload
    date_str = date.today().strftime("%Y%m%d")
    for f in args.files_to_upload:
      file_info = get_files_info(f, date_str, analysis_dict)
      payload['files'].append(file_info)

    with open("%s.%s.payload.json" % (str(uuid.uuid4()), args.wf_name), 'w') as f:
        f.write(json.dumps(payload, indent=2))



if __name__ == "__main__":
    main()

