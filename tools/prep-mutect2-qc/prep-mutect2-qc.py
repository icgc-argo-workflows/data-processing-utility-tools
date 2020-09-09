#!/usr/bin/env python3

import os
import sys
import json
import glob
from argparse import ArgumentParser
import subprocess
import re
import tarfile
import csv


def run_cmd(cmd):
    stderr, p, success = '', None, True
    try:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        stderr = p.communicate()[1].decode('utf-8')
    except Exception as e:
        print('Execution failed: %s' % e)
        success = False

    if p and p.returncode != 0:
        print('Execution failed, none zero code returned. \nSTDERR: %s' % repr(stderr), file=sys.stderr)
        success = False

    if not success:
        sys.exit(p.returncode if p.returncode else 1)

    return


def get_contamination_extra_info(file_path):
    extra_info = {}
    print(file_path)
    with open(file_path, 'r') as fp:
        for row in fp.readlines():
            if row.startswith('sample'):
                continue
            cols = row.strip().split()
            extra_info.update({
                'sample_id': cols[0],
                'contamination': float(cols[1]),
                'error': float(cols[2])
            })

    return extra_info


def main(args):
    qc_file_patterns = {
        'tumour_contamination': '*.tumour.*_metrics',
        'normal_contamination': '*.normal.*_metrics'
    }

    # only contamination metrics for now, may have more later
    description = {
        'contamination': 'Cross sample contamination estimated by GATK CalculateContamination tool'
    }

    for qc_file_pttn in qc_file_patterns:
        extra_info = {
            "description": None,
            "files_in_tgz": []
        }
        metrics = {}
        tar_name = None
        cont_metrics_file = None
        qc_files = glob.glob(qc_file_patterns[qc_file_pttn])
        for f in qc_files:
            if f.endswith('contamination_metrics'):
                cont_metrics_file = f
                tar_name = f'{f}.tgz'
            extra_info['files_in_tgz'].append(f)

        extra_info['description'] = description['contamination']

        # TODO: populate metrics info
        metrics = get_contamination_extra_info(cont_metrics_file)

        extra_info.update({"metrics": metrics})
        extra_json = f'{cont_metrics_file}.extra_info.json'
        extra_info['files_in_tgz'].append(extra_json)
        with open(extra_json, 'w') as j:
            j.write(json.dumps(extra_info, indent=2))

        cmd = f'rm -rf {tar_name} tar_dir && mkdir tar_dir && cd tar_dir && cp ../{qc_file_patterns[qc_file_pttn]} ../{extra_json} . && tar czf {tar_name} * && mv {tar_name} .. && cd .. && rm -fr tar_dir'
        run_cmd(cmd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", dest="qc_files", nargs="+", required=True, help="GATK contamination files")
    args = parser.parse_args()

    main(args)
