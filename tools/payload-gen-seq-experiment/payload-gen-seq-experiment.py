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

def get_files_info(input_file):
    payload_file = {}
    payload_file['fileName'] = input_file.get('name')
    payload_file['fileSize'] = input_file.get('size')
    payload_file['fileMd5sum'] = input_file.get('md5sum')
    payload_file['fileType'] = input_file.get('format')
    payload_file['fileAccess'] = "controlled"
    # payload_file['dataType'] = 'Sequencing Reads'
    return payload_file

def main(args):

    with open(args.user_submit_metadata, 'r') as f:
        metadata = json.load(f)

    payload = {}
    payload['analysisType'] = {
        "name": "sequencing_experiment"
    }

    payload['study'] = metadata.get('program_id')
    payload['read_group_count'] = metadata.get('read_group_count')

    payload['experiment'] = {}
    for item in ['submitter_sequencing_experiment_id', 'sequencing_center', 'platform', 'platform_model', 'library_strategy', 'sequencing_date']:
        payload['experiment'][item] = metadata.get(item)

    # get sample of the payload
    payload['sample'] = []
    sample = {}
    sample['sampleSubmitterId'] = metadata.get('submitter_sample_id')
    sample['sampleType'] = metadata.get('sample_type')
    sample['specimen'] = {}
    sample['specimen']['specimenSubmitterId'] = metadata.get('submitter_specimen_id')

    # SONG specimenType needs to be synchronized with latest ARGO clinical dictionary
    specimen_type = metadata.get('tumour_normal_designation')
    sample['specimen']['specimenType'] = specimen_type
    if 'tumour' in specimen_type.lower():
        sample['specimen']['specimenClass'] = "Tumour"
    elif 'normal' in specimen_type.lower() and 'adjacent' in specimen_type.lower():
        sample['specimen']['specimenClass'] = "Adjacent normal"
    elif 'normal' in specimen_type.lower():
        sample['specimen']['specimenClass'] = "Normal"
    else:
        sys.exit("Unknown specimen type: %s" % specimen_type)

    sample['donor'] = {}
    sample['donor']['donorSubmitterId'] = metadata.get('submitter_donor_id')
    sample['donor']['donorGender'] = metadata.get('gender')
    payload['sample'].append(sample)

    # get workflow of the payload
    payload['workflow'] = {}
    payload['workflow']['name'] = args.wf_name
    payload['workflow']['short_name'] = args.wf_short_name if args.wf_short_name is not None else args.wf_name
    payload['workflow']['version'] = args.wf_version

    # get file and read_group of payload
    payload['read_groups'] = metadata.get("read_groups")

    payload['file'] = []
    # get file of the payload
    for input_file in metadata.get("files"):
        payload['file'].append(get_files_info(input_file))


    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--user_submit_metadata", dest="user_submit_metadata",
                        help="json file containing experiment, read_group and file information submitted from user")
    parser.add_argument("-w", "--wf_name", dest="wf_name", type=str, help="workflow full name", required=True)
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str, help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str, help="workflow version")
    args = parser.parse_args()

    main(args)
