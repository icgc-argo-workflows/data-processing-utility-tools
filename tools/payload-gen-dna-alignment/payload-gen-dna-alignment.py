#!/usr/bin/env python3

import os
import sys
import json
from argparse import ArgumentParser
import hashlib
import subprocess




def get_wf_fullname(wf_short_name):
    wf_fullname = {
        "user-preprocess": "Client Side preprcess",
        "rdpc-dna-alignment": "RDPC Side DNA Alignment"
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


def get_files_info(file_to_upload, filename=None):
    payload_file = {}
    if filename:
        cmd = 'cp %s %s' % (file_to_upload, filename)
        run_cmd(cmd)
        file_to_upload = os.path.realpath(filename)
    payload_file['fileName'] = os.path.basename(file_to_upload)
    payload_file['fileType'] = file_to_upload.strip(".gz").split(".")[-1]
    payload_file['fileSize'] = calculate_size(file_to_upload)
    payload_file['fileMd5sum'] = calculate_md5(file_to_upload)
    payload_file['fileAccess'] = "controlled"
    payload_file['info'] = {"data_type": "Aligned Reads" if payload_file['fileType'] in ['bam', 'cram'] else "Aligned Reads Index"}

    return payload_file

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


def main(args):


    payload = {}


    #get inputs of the payload
    payload['inputs'] = []
    for res_file in args.input_payload:
        with open(res_file, 'r') as f:
            res_json = json.load(f)
        payload['program_id'] = res_json.get('program_id')
        payload['study'] = res_json.get('program_id')
        payload['sample'] = res_json.get('sample')

        payload['inputs'].append({'read_group_ubam_id': res_json.get('analysisId')})


    #get file of the payload
    payload['file'] = []
    payload['file'].append(get_files_info(args.file_to_upload))

    #get index files of the payload
    if os.path.exists(args.file_to_upload + ".bai"):
        payload['file'].append(get_files_info(args.file_to_upload + ".bai"))
    elif os.path.exists(args.file_to_upload + ".crai"):
        payload['file'].append(get_files_info(args.file_to_upload + ".crai"))
    else:
        sys.exit('\n%s: Missing index file')

    #get workflow info of the payload
    payload['workflow'] = {}
    payload['workflow']['name'] = get_wf_fullname(args.wf_short_name)
    payload['workflow']['short_name'] = args.wf_short_name
    payload['workflow']['version'] = args.wf_version

    with open("payload.json", 'w') as f:
        f.write(json.dumps(payload, indent=2))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file_to_upload", dest="file_to_upload", type=str, help="File to upload to server")
    parser.add_argument("-a", "--input_payload", dest="input_payload", help="Input payloads for the analysis",
                        type=str, nargs='+')
    parser.add_argument("-c", "--wf_short_name", dest="wf_short_name", type=str, choices=['sanger-wxs', 'sanger-wgs', 'broad-mutect2'],
                        help="workflow short name")
    parser.add_argument("-v", "--wf_version", dest="wf_version", type=str,
                        help="workflow version")
    args = parser.parse_args()

    main(args)
