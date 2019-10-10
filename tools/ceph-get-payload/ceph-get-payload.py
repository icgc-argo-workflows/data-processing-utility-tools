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
                                                args.program_id,
                                                args.submitter_donor_id,
                                                args.submitter_sample_id,
                                                'normal' if 'normal' in args.tumour_normal_designation.lower() else 'tumour'
                                            )

    if args.bundle_type in ['lane_seq_submission', 'lane_seq_qc']:
        if not args.submitter_read_group_id:
            sys.exit("Missing the information of submitter_read_group_id!")
        submitter_read_group_id = args.submitter_read_group_id

        object_key = "%s/lane_seq_submission/%s" % (path_prefix, submitter_read_group_id)

    elif args.bundle_type == 'dna_alignment':
        if not args.seq_format:
            sys.exit("Missing the information of sequence format!")
        seq_format = args.seq_format

        object_key = "%s/dna_alignment/%s" % (path_prefix, seq_format)

    elif args.bundle_type in ['sequencing_experiment', 'dna_alignment_qc', 'sanger_ssm_call']:

        object_key = "%s/%s" % (path_prefix, args.bundle_type)

    else:
        sys.exit('Unknown or unimplemented bundle_type: %s' % args.bundle_type)

    ret = run_command("aws --endpoint-url %s s3 ls s3://%s/%s/  --recursive | grep '\.json$' | sort | tail -n 1 | awk '{print $4}'" % (
        args.endpoint_url,
        args.bucket_name,
        object_key))

    recent_payload = ret.stdout.decode('ascii').rstrip('\n')
    
    p = run_command('aws --endpoint-url %s s3 cp s3://%s/%s .' % (
        args.endpoint_url,
        args.bucket_name,
        recent_payload))

    if p.returncode != 0:
        sys.exit('Get payload failed. Err: %s' % p.stderr)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--endpoint-url", dest="endpoint_url", type=str)
    parser.add_argument("-n", "--bucket-name", dest="bucket_name", type=str)
    parser.add_argument("-y", "--bundle-type", dest="bundle_type", type=str)
    parser.add_argument("-c", "--s3-credential-file", dest="s3_credential_file", type=str)
    parser.add_argument("-r", "--submitter-read-group-id", dest="submitter_read_group_id", type=str)
    parser.add_argument("-f", "--seq-format", dest="seq_format", type=str)
    parser.add_argument("-l", "--library-strategy", dest="library_strategy", type=str)
    parser.add_argument("-p", "--program-id", dest="program_id", type=str)
    parser.add_argument("-d", "--submitter-donor-id", dest="submitter_donor_id", type=str)
    parser.add_argument("-s", "--submitter-sample-id", dest="submitter_sample_id", type=str)
    parser.add_argument("-t", "--tumour-normal-designation", dest="tumour_normal_designation", type=str)

    args = parser.parse_args()

    main(args)
