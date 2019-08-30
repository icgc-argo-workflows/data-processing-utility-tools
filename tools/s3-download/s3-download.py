#!/usr/bin/env python3

import os
import sys
import json
from argparse import ArgumentParser
import subprocess


def run_command(cmd):
    return subprocess.run(cmd, capture_output=True, shell=True)


def object_exists(endpoint_url, object_key):
    ret = run_command('aws --endpoint-url %s s3 ls %s' % (endpoint_url, object_key))
    if ret.returncode == 0:
        return True
    else:
        return False


def copy_credential_file(credential_file):
    run_command('mkdir ~/.aws')
    run_command('cp %s ~/.aws/credentials' % credential_file)


def main(args):

    copy_credential_file(args.s3_credential_file)

    with open(args.payload_json) as f:
        payload = json.load(f)

    bundle_id = payload['id']

    path_prefix = "PCAWG2/%s/%s/%s/%s.%s" % (
                                                payload['info']['library_strategy'],
                                                payload['program'],
                                                payload['info']['donor_submitter_id'],
                                                payload['info']['sample_submitter_id'],
                                                'normal' if 'normal' in payload['info']['specimen_type'].lower() else 'tumour'
                                            )

    if payload['type'] == 'lane_seq_submission':
        read_group_submitter_id = payload['inputs']['read_group_submitter_id']

        """ don't do this for now
        payload_object_key = "%s/lane_seq_submission/%s/%s.json" % (
            path_prefix,
            read_group_submitter_id,
            bundle_id)
        if not object_exists(args.endpoint_url, 's3://%s/%s' % (args.bucket_name, payload_object_key)):
            sys.exit('Not able to access object store, or payload object does not exist: s3://%s/%s' % (args.bucket_name, payload_object_key))
        """

        for object in payload['files']:
            object_id = payload['files'][object]['object_id']
            filename = payload['files'][object]['name']
            object_key = "%s/lane_seq_submission/%s/%s/%s" % (path_prefix,
                                                                read_group_submitter_id,
                                                                bundle_id,
                                                                object_id)

            p = run_command('aws --endpoint-url %s s3 cp s3://%s/%s %s' % (
                    args.endpoint_url,
                    args.bucket_name,
                    object_key,
                    filename))

            if p.returncode != 0:
                sys.exit('Object download failed: %s; err: %s' % (object_key, p.stderr))

    elif payload['type'] == 'dna_alignment':

        """
        payload_object_key = "%s/dna_alignment/%s/%s.json" % (
            path_prefix,
            bam_cram,
            bundle_id)
        if not object_exists(args.endpoint_url, 's3://%s/%s' % (args.bucket_name, payload_object_key)):
            sys.exit('Not able to access object store, or payload object does not exist: s3://%s/%s' % (args.bucket_name, payload_object_key))
        """

        for object in payload['files']:
            object_id = payload['files'][object]['object_id']
            filename = payload['files'][object]['name']
            bam_cram = 'bam' if filename.endswith('bam') or filename.endswith('bai') else 'cram'
            object_key = "%s/dna_alignment/%s/%s/%s" % (path_prefix,
                                                        bam_cram,
                                                        bundle_id,
                                                        object_id)

            p = run_command('aws --endpoint-url %s s3 cp s3://%s/%s %s' % (
                    args.endpoint_url,
                    args.bucket_name,
                    object_key,
                    filename))

            if p.returncode != 0:
                sys.exit('Object download failed: %s; err: %s' % (object_key, p.stderr))

    elif payload['type'] == 'sanger_ssm_call':
        """
        payload_object_key = "%s/dna_alignment/%s/%s.json" % (
            path_prefix,
            bam_cram,
            bundle_id)
        if not object_exists(args.endpoint_url, 's3://%s/%s' % (args.bucket_name, payload_object_key)):
            sys.exit('Not able to access object store, or payload object does not exist: s3://%s/%s' % (args.bucket_name, payload_object_key))
        """

        for object in payload['files']:
            object_id = payload['files'][object]['object_id']
            filename = payload['files'][object]['name']
            object_key = "%s/sanger_ssm_call/%s/%s" % (path_prefix,
                                                       bundle_id,
                                                       object_id)

            p = run_command('aws --endpoint-url %s s3 cp s3://%s/%s %s' % (
                args.endpoint_url,
                args.bucket_name,
                object_key,
                filename))

            if p.returncode != 0:
                sys.exit('Object upload failed: %s; err: %s' % (object_key, p.stderr))

    else:
        sys.exit('Unknown or unimplemented bundle_type: %s' % args.bundle_type)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--endpoint-url", dest="endpoint_url")
    parser.add_argument("-b", "--bucket-name", dest="bucket_name")
    parser.add_argument("-p", "--payload-json", dest="payload_json", type=str)
    parser.add_argument("-c", "--s3-credential-file", dest="s3_credential_file")
    args = parser.parse_args()

    main(args)
