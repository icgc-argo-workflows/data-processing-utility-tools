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

 Authors:
   Linda Xiang <linda.xiang@oicr.on.ca>
   Junjun Zhang <junjun.zhang@oicr.on.ca>
 """


import sys
import json
from argparse import ArgumentParser


def get_specimen_type_class(metadata):
    # SONG specimenType and specimenClass need to be synchronized with latest ARGO clinical dictionary,
    # before that, we will use this function to perform approximate translation as a temporary WORKAROUND
    tumour_normal_designation = metadata.get('tumour_normal_designation')
    specimen_tissue_source = metadata.get('specimen_tissue_source')

    if 'tumour' in tumour_normal_designation.lower():
        specimen_class = "Tumour"
        if 'recurrent tumour' in tumour_normal_designation.lower():
            if 'solid tissue' in specimen_tissue_source.lower():
                specimen_type = 'Recurrent tumour - solid tissue'
            elif 'other' in specimen_tissue_source.lower():
                specimen_type = 'Recurrent tumour - other'
            else:
                specimen_type = tumour_normal_designation
        elif 'metastatic tumour' in tumour_normal_designation.lower():
            if 'lymph node' in specimen_tissue_source.lower():
                specimen_type = 'Metastatic tumour - lymph node'
            elif 'other' in specimen_tissue_source.lower():
                specimen_type = 'Metastatic tumour - other'
            else:
                specimen_type = tumour_normal_designation
        else:
            if 'solid tissue' in specimen_tissue_source.lower():
                specimen_type = 'Primary tumour - solid tissue'
            elif 'lymph node' in specimen_tissue_source.lower():
                specimen_type = 'Primary tumour - lymph node'
            elif 'other' in specimen_tissue_source.lower():
                specimen_type = 'Primary tumour - other'
            else:
                specimen_type = tumour_normal_designation
    elif 'normal' in tumour_normal_designation.lower() and 'adjacent' in tumour_normal_designation.lower():
        specimen_class = "Adjacent normal"
        specimen_type = tumour_normal_designation
    elif 'normal' in tumour_normal_designation.lower():
        specimen_class = "Normal"
        if 'solid tissue' in specimen_tissue_source.lower():
            specimen_type = 'Normal - solid tissue'
        elif 'blood derived' in specimen_tissue_source.lower():
            specimen_type = 'Normal - blood derived'
        elif 'bone marrow' in specimen_tissue_source.lower():
            specimen_type = 'Normal - bone marrow'
        elif 'buccal cell' in specimen_tissue_source.lower():
            specimen_type = 'Normal - buccal cell'
        elif 'lymph node' in specimen_tissue_source.lower():
            specimen_type = 'Normal - lymph node'
        elif 'other' in specimen_tissue_source.lower():
            specimen_type = 'Normal - other'
        else:
            specimen_type = tumour_normal_designation
    else:
        sys.exit("Unknown tumour_normal_designation: %s" % tumour_normal_designation)

    return {
        'specimenType': specimen_type,
        'specimenClass': specimen_class
    }


def main(args):
    with open(args.user_submit_metadata, 'r') as f:
        metadata = json.load(f)

    payload = {
        'analysisType': {
            'name': 'sequencing_experiment'
        },
        'study': metadata.get('program_id'),
        'submitter_sequencing_experiment_id': metadata.get('submitter_sequencing_experiment_id'),
        'experiment': {
            'sequencing_center': metadata.get('sequencing_center'),
            'platform': metadata.get('platform'),
            'platform_model': metadata.get('platform_model'),
            'library_strategy': metadata.get('library_strategy'),
            'sequencing_date': metadata.get('sequencing_date')
        },
        'read_group_count': metadata.get('read_group_count'),
        'workflow': {
            'name': args.wf_name,
            'short_name': args.wf_short_name if args.wf_short_name is not None else args.wf_name,
            'version': args.wf_version,
            'run_id': args.wf_run
        },
        'read_groups': [],
        'sample': [],
        'file': []
    }

    # get sample of the payload
    sample = {
        'sampleSubmitterId': metadata.get('submitter_sample_id'),
        # 'submitter_matched_normal_sample_id': metadata.get('submitter_matched_normal_sample_id'),  # SONG does not support this yet
        'sampleType': metadata.get('sample_type'),
        'specimen': {
            'specimenSubmitterId': metadata.get('submitter_specimen_id')
        },
        'donor': {
            'donorSubmitterId': metadata.get('submitter_donor_id'),
            'donorGender': metadata.get('gender')
        }
    }

    sample['specimen'].update(get_specimen_type_class(metadata))

    payload['sample'].append(sample)

    # get file of the payload
    for input_file in metadata.get("files"):
        payload['file'].append(
            {
                'fileName': input_file.get('name'),
                'fileSize': input_file.get('size'),
                'fileMd5sum': input_file.get('md5sum'),
                'fileType': input_file.get('format'),
                'fileAccess': 'controlled',
                # 'dataType': 'Sequencing Reads'  # SONG does not accept this yet
            }
        )

    for rg in metadata.get("read_groups"):
        rg.pop('type')  # remove 'type' field
        rg.pop('submitter_sequencing_experiment_id')  # remove 'submitter_sequencing_experiment_id' field
        payload['read_groups'].append(rg)

    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--user-submit-metadata", dest="user_submit_metadata", required=True,
                        help="json file containing experiment, read_group and file information submitted from user")
    parser.add_argument("-w", "--wf-name", dest="wf_name", type=str, help="workflow full name", required=True)
    parser.add_argument("-c", "--wf-short-name", dest="wf_short_name", type=str, help="workflow short name")
    parser.add_argument("-v", "--wf-version", dest="wf_version", type=str, required=True, help="workflow version")
    parser.add_argument("-r", "--wf-run", dest="wf_run", type=str, required=True, help="workflow run ID")
    args = parser.parse_args()

    main(args)
