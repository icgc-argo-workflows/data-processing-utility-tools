#!/usr/bin/env python3

import os
import sys
import json
import re
from argparse import ArgumentParser
import hashlib
import copy
import subprocess
import uuid
import datetime


def get_app_info(wf_name, data_type):
    app_info = {
        "sanger-wxs": {
            "snv": ["CaVEMan"],
            "indel": ["Pindel"]
        },
        "sanger-wgs": {
            "snv": ["CaVEMan"],
            "indel": ["Pindel"],
            "cnv": ["ASCAT"],
            "sv": ["BRASS"]
        },
        "broad-mutect2": {
            "snv-indel": ["mutect2"]
        }
    }

    if app_info.get(wf_name) and app_info.get(wf_name).get(data_type):
        return app_info.get(wf_name).get(data_type)
    else:
        sys.exit("Unknown workflow or data type")


def get_analysis_type(data_type):
    analysis_type = {
        "snv": "Simple somatic mutation calling",
        "indel": "Simple somatic mutation calling",
        "snv-indel": "Simple somatic mutation calling",
        "cnv": "Copy number somatic mutation calling",
        "sv": "Structural somatic mutation calling"
    }

    return analysis_type.get(data_type)

def get_uuid5(bid, fid):
    uuid5 = str(uuid.uuid5(uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"), "%s/%s" % (bid, fid)))
    return uuid5


def calculate_size(file_path):
    return os.stat(file_path).st_size

def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()

def get_files_info(file_to_upload, filename=None):
    payload_files = {}
    if filename:
        cmd = 'cp %s %s' % (file_to_upload, filename)
        run_cmd(cmd)
        file_to_upload = os.path.realpath(filename)
    payload_files['name'] = os.path.basename(file_to_upload)
    payload_files['path'] = file_to_upload
    payload_files['size'] = calculate_size(file_to_upload)
    payload_files['checksum'] = calculate_md5(file_to_upload)

    return payload_files

def run_cmd(cmd):
    stdout, stderr, p, success = '', '', None, True
    try:
        p = subprocess.Popen([cmd],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        p.communicate()
    except Exception as e:
        print('Execution failed: %s' % e)
        success = False

    if p and p.returncode != 0:
        print('Execution failed, none zero code returned.')
        success = False

    if not success:
        sys.exit(p.returncode if p.returncode else 1)

    return


def main(args):

    if args.bundle_type == 'lane_seq_submission':
        with open(args.input_metadata_lane_seq, 'r') as f:
            metadata = json.load(f)

        if metadata.get("input_seq_format") == 'FASTQ':
            read_group = metadata.get("read_groups")

            payload_template_url = "https://raw.githubusercontent.com/icgc-argo/argo-metadata-schemas/%s/schemas/_example_docs/36.lane_seq_submission.01.ok.json" % args.payload_schema_version
            cmd = "curl -o template --retry 10 %s" % payload_template_url
            run_cmd(cmd)

            with open("template", "r") as f:
                payload = json.load(f)

            payload['program_id'] = metadata.get('program_id')

            #get inputs of the payload
            for rg in read_group:
                rg_id = rg.get("submitter_read_group_id")
                rg_fname = "".join([c if re.match(r"[a-zA-Z0-9\-_]", c) else "_" for c in rg_id])
                if not rg_fname in args.file_to_upload: continue
                payload['inputs']['submitter_read_group_id'] = rg_id
                payload['inputs']['files']['fastq'] = rg.get('files')

        elif metadata.get("input_seq_format") == 'BAM':
            files = metadata.get("files")

            payload_template_url = "https://raw.githubusercontent.com/icgc-argo/argo-metadata-schemas/%s/schemas/_example_docs/35.lane_seq_submission.01.ok.json" % args.payload_schema_version
            cmd = "curl -o template --retry 10 %s" % payload_template_url
            run_cmd(cmd)

            with open("template", "r") as f:
                payload = json.load(f)

            payload['program_id'] = metadata.get('program_id')

            # get inputs of the payload
            for input_file in files:
                for rg in input_file.get('read_groups'):
                    rg_id = rg.get("submitter_read_group_id")
                    rg_fname = "".join([c if re.match(r"[a-zA-Z0-9\-_]", c) else "_" for c in rg_id])
                    if not rg_fname in args.file_to_upload: continue
                    payload['inputs']['submitter_read_group_id'] = rg_id
                    payload['inputs']['files']['bam'] = copy.deepcopy(input_file)
                    payload['inputs']['files']['bam'].pop('read_groups')

        else:
            sys.exit('\n%s: Input files format are not FASTQ or BAM')

        #get files of the payload
        payload['files']['bam_file'].update(get_files_info(args.file_to_upload))

        payload['files']['bam_file'].pop('_final_doc', None)
        payload['files']['bam_file'].pop('_mocked_system_properties', None)

    elif args.bundle_type == 'dna_alignment':
        payload_template_url = "https://raw.githubusercontent.com/icgc-argo/argo-metadata-schemas/%s/schemas/_example_docs/40.dna_alignment.01.ok.json" % args.payload_schema_version
        cmd = "curl -o template --retry 10 %s" % payload_template_url
        run_cmd(cmd)

        with open("template", "r") as f:
            payload = json.load(f)

        # get inputs of the payload
        lane_seq_list = []
        for res_file in args.input_metadata_aligned_seq:
            lane_seq = {}
            with open(res_file, 'r') as f:
                res_json = json.load(f)
            payload['program_id'] = res_json.get('program_id')

            lane_seq['lane_seq_submission_id'] = res_json.get('id')
            lane_seq['files'] = {}
            lane_seq['files']['lane_seq'] = res_json['files']['bam_file']

            lane_seq['files']['lane_seq'].update({"bundle_id": res_json.get('id')})

            lane_seq_list.append(lane_seq)

        payload['inputs']['lane_seq'] = lane_seq_list

        #get files of the payload
        payload['files']['aligned_seq'].update(get_files_info(args.file_to_upload))

        #get index files of the payload
        if os.path.exists(args.file_to_upload + ".bai"):
            payload['files']['aligned_seq_index'].update(get_files_info(args.file_to_upload + ".bai"))
        elif os.path.exists(args.file_to_upload + ".crai"):
            payload['files']['aligned_seq_index'].update(get_files_info(args.file_to_upload + ".crai"))
        else:
            sys.exit('\n%s: Missing index file')

        payload['files']['aligned_seq'].pop('_final_doc', None)
        payload['files']['aligned_seq'].pop('_mocked_system_properties', None)
        payload['files']['aligned_seq_index'].pop('_final_doc', None)
        payload['files']['aligned_seq_index'].pop('_mocked_system_properties', None)

    elif args.bundle_type == 'somatic_variant_call':
        payload_template_url = "https://raw.githubusercontent.com/icgc-argo/argo-metadata-schemas/%s/schemas/_example_docs/60.somatic_variant_call.01-sanger-wxs-snv.ok.json" % args.payload_schema_version
        cmd = "curl -o template --retry 10 %s" % payload_template_url
        run_cmd(cmd)

        with open("template", "r") as f:
            payload = json.load(f)

        # update analysis of the payload
        payload['analysis']['analysis_type'] = get_analysis_type(args.data_type)
        payload['analysis']['tool']['name'] = "icgc-argo/%s-variant-calling" % args.wf_short_name
        payload['analysis']['tool']['short_name'] = args.wf_short_name
        payload['analysis']['tool']['version'] = args.wf_version
        payload['analysis']['tool']['included_apps'] = get_app_info(args.wf_short_name, args.data_type)

        # get inputs of the payload
        for res_file in args.input_metadata_aligned_seq:
            input_file = {}
            with open(res_file, 'r') as f:
                res_json = json.load(f)
            payload['program_id'] = res_json.get('program_id')

            input_file['dna_alignment_id'] = res_json.get('id')
            input_file['files'] = {}
            input_file['files']['aligned_dna_seq'] = res_json['files']['aligned_seq']
            input_file['files']['aligned_dna_seq'].update({"bundle_id": res_json.get('id')})
            if input_file['files']['aligned_dna_seq']['name'].endswith('bam'):
                input_file['files']['aligned_dna_seq'].update({"secondary_file": '.bai'})
            elif input_file['files']['aligned_dna_seq']['name'].endswith('cram'):
                input_file['files']['aligned_dna_seq'].update({"secondary_file": '.crai'})
            else:
                sys.exit('\n%s: Unknown file type')

            if res_json.get('info') and res_json.get('info').get('tumour_normal_designation'):
                if 'normal' in res_json.get('info').get('tumour_normal_designation').lower():
                    payload['inputs']['normal'] = input_file
                else:
                    payload['inputs']['tumour'] = input_file
                    uuid_prefix = get_uuid5(res_json.get('info').get('program_id'), res_json.get('info').get('submitter_sample_id'))
                    filename = '.'.join([uuid_prefix, res_json.get('info').get('library_strategy').lower(),
                                         datetime.date.today().strftime("%Y%m%d"),
                                         args.wf_short_name, args.wf_version, 'somatic',
                                         args.data_type, 'vcf', 'gz'])
            else:
                sys.exit('\n%s: Not enough information to proceed!')

        # get files of the payload
        payload['files']['vcf'].update(get_files_info(args.file_to_upload, filename))

        # get index files of the payload
        if os.path.exists(args.file_to_upload + ".tbi"):
            payload['files']['vcf_index'].update(get_files_info(args.file_to_upload + ".tbi", filename+".tbi"))
        elif os.path.exists(args.file_to_upload + ".idx"):
            payload['files']['vcf_index'].update(get_files_info(args.file_to_upload + ".idx", filename+".idx"))
        else:
            sys.exit('\n%s: Missing index file')

        payload['files']['vcf'].pop('_final_doc', None)
        payload['files']['vcf'].pop('_mocked_system_properties', None)
        payload['files']['vcf_index'].pop('_final_doc', None)
        payload['files']['vcf_index'].pop('_mocked_system_properties', None)


    else:
        sys.exit('\n%s: Unknown bundle_type')


    payload.pop('_final_doc', None)
    payload.pop('_mocked_system_properties', None)


    payload_fname = ".".join([args.bundle_type, os.path.basename(args.file_to_upload), 'json'])
    with open(payload_fname, 'w') as f:
        f.write(json.dumps(payload))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--bundle_type", dest="bundle_type", type=str,
                        help="Payload type")
    parser.add_argument("-p", "--payload_schema_version", dest="payload_schema_version", help="release version of payload schema")
    parser.add_argument("-m", "--input_metadata_lane_seq", dest="input_metadata_lane_seq",
                        help="json file containing experiment, read_group and file information for sequence preprocessing")
    parser.add_argument("-f", "--file_to_upload", dest="file_to_upload", type=str, help="File to upload to server")
    parser.add_argument("-a", "--input_metadata_aligned_seq", dest="input_metadata_aligned_seq", help="Analysis of lane seq submission",
                        type=str, nargs='+')
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str,
                        help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str,
                        help="workflow version")
    parser.add_argument("-d", "--data_type", dest="data_type", type=str,
                        help="data type")
    args = parser.parse_args()

    main(args)
