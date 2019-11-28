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


import sys
import json
from argparse import ArgumentParser


def get_wf_fullname(wf_short_name):
    wf_fullname = {
        "dna-seq-alignment": "dna-seq-alignment"
    }
    return wf_fullname.get(wf_short_name)



def get_files_info(input_file):
    payload_file = {}
    payload_file['fileName'] = input_file.get('name')
    payload_file['fileSize'] = input_file.get('size')
    payload_file['fileMd5sum'] = input_file.get('checksum')
    payload_file['fileType'] = input_file.get('format')
    payload_file['fileAccess'] = "controlled"
    payload_file['info'] = {}
    payload_file['info']['submitter_read_group_id'] = input_file.get('submitter_read_group_id')
    payload_file['info']['data_type'] = input_file.get('type')
    return payload_file

def main(args):

    with open(args.user_submit_metadata, 'r') as f:
        metadata = json.load(f)

    payload = {}
    payload['analysisType'] = {
        "name": "sequencing_experiment"
    }

    payload['program_id'] = metadata.get('program_id')
    payload['study'] = metadata.get('program_id')
    for item in ['submitter_sequencing_experiment_id', 'sequencing_center', 'platform', 'platform_model', 'library_strategy', 'sequencing_date', 'read_group_count']:
        payload[item] = metadata.get(item)

    # get sample of the payload
    payload['sample'] = []
    sample = {}
    sample['sampleSubmitterId'] = metadata.get('submitter_sample_id')
    sample['sampleType'] = "DNA"
    sample['specimen'] = {}
    sample['specimen']['specimenSubmitterId'] = metadata.get('submitter_specimen_id', None)
    sample['specimen']['specimenClass'] = "Tumour"
    sample['specimen']['specimenType'] = metadata.get('tumour_normal_designation')
    sample['donor'] = {}
    sample['donor']['donorSubmitterId'] = metadata.get('submitter_donor_id')
    sample['donor']['donorGender'] = metadata.get('gender', None)
    payload['sample'].append(sample)

    # get workflow of the payload
    payload['workflow'] = {}
    payload['workflow']['name'] = get_wf_fullname(args.wf_short_name)
    payload['workflow']['short_name'] = args.wf_short_name
    payload['workflow']['version'] = args.wf_version

    # get file and read_group of payload
    payload['read_group'] = []
    payload['file'] = []
    if metadata.get("input_seq_format") == 'FASTQ':
        read_group = metadata.get("read_groups")

        #get read_group of the payload
        for rg in read_group:
            rg_item = {}
            for item in ['submitter_read_group_id', 'platform_unit', 'library_name', 'is_paired_end', 'read_length_r1', 'read_length_r2', 'insert_size', 'sample_barcode']:
                rg_item[item] = rg.get(item, None)
            payload['read_group'].append(rg_item)

            # get file of the payload
            for input_file in rg.get('files'):
                payload['file'].append(get_files_info(input_file))

    elif metadata.get("input_seq_format") == 'BAM':
        files = metadata.get("files")

        # get file of the payload
        for input_file in files:
            payload['file'].append(get_files_info(input_file))
            # get read_group of the payload
            for rg in input_file.get('read_groups'):
                rg_item = {}
                for item in ['submitter_read_group_id', 'platform_unit', 'is_paired_end', 'read_length_r1',
                             'read_length_r2', 'insert_size', 'sample_barcode']:
                    rg_item[item] = rg.get(item, None)
                payload['read_group'].append(rg_item)

    else:
        sys.exit('\n%s: Input files format are not FASTQ or BAM')

    payload['experiment'] = {}

    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--user_submit_metadata", dest="user_submit_metadata",
                        help="json file containing experiment, read_group and file information submitted from user")
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str,
                        help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str,
                        help="workflow version")
    args = parser.parse_args()

    main(args)
