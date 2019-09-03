#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
import subprocess


def run_command(cmd):
    return subprocess.run(cmd, capture_output=True, shell=True)

def copy_credential_file(credential_file):
    run_command('mkdir ~/.aws')
    run_command('cp %s ~/.aws/credentials' % credential_file)


def main(args):

    copy_credential_file(args.s3_credential_file)

    path_prefix = "PCAWG2/%s/%s/%s/%s.%s" % (
                                                args.library_strategy,
                                                args.program,
                                                args.donor_submitter_id,
                                                args.sample_submitter_id,
                                                'normal' if 'normal' in args.specimen_type.lower() else 'tumour'
                                            )

    if args.bundle_type in ['lane_seq_submission', 'lane_seq_qc']:
        if not args.read_group_submitter_id:
            sys.exit("Missing the information of read_group_submitter_id!")
        read_group_submitter_id = args.read_group_submitter_id

        object_key = "%s/lane_seq_submission/%s" % (path_prefix, read_group_submitter_id)

    elif args.bundle_type == 'dna_alignment':
        if not args.seq_format:
            sys.exit("Missing the information of sequence format!")
        seq_format = args.seq_format

        object_key = "%s/dna_alignment/%s" % (path_prefix, seq_format)

    elif args.bundle_type in ['sequencing_experiment', 'dna_alignment_qc', 'sanger_ssm_call']:

        object_key = "%s/%s" % (path_prefix, args.bundle_type)

    else:
        sys.exit('Unknown or unimplemented bundle_type: %s' % args.bundle_type)

    p = run_command('aws --endpoint-url %s s3 cp s3://%s/%s/ . --recursive --exclude "*" --include "*.json"' % (
        args.endpoint_url,
        args.bucket_name,
        object_key))

    if p.returncode != 0:
        sys.exit('Get payload failed. Err: %s' % p.stderr)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--endpoint-url", dest="endpoint_url", type=str)
    parser.add_argument("-n", "--bucket-name", dest="bucket_name", type=str)
    parser.add_argument("-y", "--bundle-type", dest="bundle_type", type=str)
    parser.add_argument("-c", "--s3-credential-file", dest="s3_credential_file", type=str)
    parser.add_argument("-r", "--read-group-submitter-id", dest="read_group_submitter_id", type=str)
    parser.add_argument("-f", "--seq-format", dest="seq_format", type=str)
    parser.add_argument("-l", "--library-strategy", dest="library_strategy", type=str)
    parser.add_argument("-p", "--program", dest="program", type=str)
    parser.add_argument("-d", "--donor-submitter-id", dest="donor_submitter_id", type=str)
    parser.add_argument("-s", "--sample-submitter-id", dest="sample_submitter_id", type=str)
    parser.add_argument("-t", "--specimen-type", dest="specimen_type", type=str)

    args = parser.parse_args()

    main(args)