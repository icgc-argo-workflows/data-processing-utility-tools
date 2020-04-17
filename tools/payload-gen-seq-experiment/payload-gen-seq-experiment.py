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


import uuid
import json
from argparse import ArgumentParser


def empty_str_to_null(metadata):
    for k in metadata:
        if k in ['read_groups', 'files']:
            for i in range(len(metadata[k])):
                empty_str_to_null(metadata[k][i])
        if isinstance(metadata[k], str) and metadata[k] in ["", "_NULL_"]:
            metadata[k] = None


def main(args):
    with open(args.user_submit_metadata, 'r') as f:
        metadata = json.load(f)

    empty_str_to_null(metadata)

    payload = {
        'analysisType': {
            'name': 'sequencing_experiment'
        },
        'studyId': metadata.get('program_id'),
        'experiment': {
            'submitter_sequencing_experiment_id': metadata.get('submitter_sequencing_experiment_id'),
            'sequencing_center': metadata.get('sequencing_center'),
            'platform': metadata.get('platform'),
            'platform_model': metadata.get('platform_model'),
            'experimental_strategy': metadata.get('experimental_strategy'),
            'sequencing_date': metadata.get('sequencing_date')
        },
        'read_group_count': metadata.get('read_group_count'),
        'read_groups': [],
        'samples': [],
        'files': []
    }

    # get sample of the payload
    sample = {
        'submitterSampleId': metadata.get('submitter_sample_id'),
        'matchedNormalSubmitterSampleId': metadata.get('submitter_matched_normal_sample_id'),
        'sampleType': metadata.get('sample_type'),
        'specimen': {
            'submitterSpecimenId': metadata.get('submitter_specimen_id'),
            'tumourNormalDesignation': metadata.get('tumour_normal_designation'),
            'specimenTissueSource': metadata.get('specimen_tissue_source'),
            'specimenType': metadata.get('specimen_type')
        },
        'donor': {
            'submitterDonorId': metadata.get('submitter_donor_id'),
            'gender': metadata.get('gender')
        }
    }

    payload['samples'].append(sample)

    # get file of the payload
    for input_file in metadata.get("files"):
        payload['files'].append(
            {
                'fileName': input_file.get('name'),
                'fileSize': input_file.get('size'),
                'fileMd5sum': input_file.get('md5sum'),
                'fileType': input_file.get('format'),
                'fileAccess': 'controlled',
                'dataType': 'submitted_reads'
            }
        )

    for rg in metadata.get("read_groups"):
        rg.pop('type')  # remove 'type' field
        rg.pop('submitter_sequencing_experiment_id')  # remove 'submitter_sequencing_experiment_id' field
        payload['read_groups'].append(rg)

    with open("%s.sequencing_experiment.payload.json" % str(uuid.uuid4()), 'w') as f:
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
