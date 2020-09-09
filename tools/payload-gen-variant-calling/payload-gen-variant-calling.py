#!/usr/bin/env python3

"""
 Copyright (c) 2019-2020, Ontario Institute for Cancer Research (OICR).

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
   Junjun Zhang <junjun.zhang@oicr.on.ca>
 """

import os
import sys
import uuid
import json
import hashlib
import copy
import re
import tarfile
from datetime import date
from argparse import ArgumentParser


variant_type_to_data_type_etc = {
    'snv': ['Simple Nucleotide Variation', 'Raw SNV Calls', ['CaVEMan'], ['Mutect2']],   # dataCategory, dataType, analysis_tools
    'indel': ['Simple Nucleotide Variation', 'Raw InDel Calls', ['Pindel'], ['Mutect2']],
    'cnv': ['Copy Number Variation', 'Raw CNV Calls', ['ASCAT']],
    'sv': ['Structural Variation', 'Raw SV Calls', ['BRASS']],
    'caveman-supplement': ['Simple Nucleotide Variation', 'Variant Calling Supplement', ['CaVEMan']],
    'pindel-supplement': ['Simple Nucleotide Variation', 'Variant Calling Supplement', ['Pindel']],
    'ascat-supplement': ['Copy Number Variation', 'Variant Calling Supplement', ['ASCAT']],
    'brass-supplement': ['Structural Variation', 'Variant Calling Supplement', ['BRASS']],
    'timings-supplement': [None, 'Variant Calling Supplement', ['CaVEMan', 'Pindel', 'ASCAT', 'BRASS']],
    'bas_metrics': ['Quality Control Metrics', 'Alignment QC', ['bas_stats']],
    'contamination_metrics': ['Quality Control Metrics', 'Cross Sample Contamination', ['verifyBamHomChk'], ['CalculateContamination']],
    'ascat_metrics': ['Quality Control Metrics', 'Ploidy and Purity Estimation', ['ASCAT']],
    'genotyped_gender_metrics': ['Quality Control Metrics', 'Genotyping Inferred Gender', ['compareBamGenotypes']],
}

workflow_full_name = {
    'sanger-wgs-variant-calling': 'Sanger WGS Variant Calling',
    'sanger-wxs-variant-calling': 'Sanger WXS Variant Calling',
    'gatk-mutect2-variant-calling': 'GATK Mutect2 Variant Calling'
}

def calculate_size(file_path):
    return os.stat(file_path).st_size


def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_files_info(file_to_upload, wf_short_name,  wf_version, somatic_or_germline, normal_analysis, tumour_analysis):
    file_info = {
        'fileType': 'VCF' if file_to_upload.endswith('.vcf.gz') else file_to_upload.split(".")[-1].upper(),
        'fileSize': calculate_size(file_to_upload),
        'fileMd5sum': calculate_md5(file_to_upload),
        'fileAccess': 'controlled',
        'info': {}
    }

    if somatic_or_germline == 'Somatic':
        metadata = tumour_analysis
    elif somatic_or_germline == 'Germline':
        metadata = normal_analysis
    else:
        pass  # should never happen

    experimental_strategy = metadata['experiment']['experimental_strategy'].lower() if 'experimental_strategy' in metadata['experiment'] else metadata['experiment']['library_strategy'].lower()
    date_str = date.today().strftime("%Y%m%d")

    variant_type = ''
    if wf_short_name in (['sanger-wgs', 'sanger-wxs']):
        fname_sample_part = metadata['samples'][0]['sampleId']
        if file_to_upload.endswith('.flagged.muts.vcf.gz') or file_to_upload.endswith('.flagged.muts.vcf.gz.tbi'):
            variant_type = 'snv'
        elif file_to_upload.endswith('.flagged.vcf.gz') or file_to_upload.endswith('.flagged.vcf.gz.tbi'):
            variant_type = 'indel'
        elif file_to_upload.endswith('.copynumber.caveman.vcf.gz') or file_to_upload.endswith('.copynumber.caveman.vcf.gz.tbi'):
            variant_type = 'cnv'
        elif file_to_upload.endswith('.annot.vcf.gz') or file_to_upload.endswith('.annot.vcf.gz.tbi'):
            variant_type = 'sv'
        elif file_to_upload.endswith('-supplement.tgz'):
            variant_type = file_to_upload.split(".")[-2]
        elif file_to_upload.endswith('_metrics.tgz'):
            variant_type = file_to_upload.split(".")[-2]
            if re.match(r'.+?\.normal.contamination_metrics.tgz', file_to_upload) \
                    or (re.match(r'.+?\.normal.bas_metrics.tgz', file_to_upload)):
                fname_sample_part = normal_analysis['samples'][0]['sampleId']
        else:
            sys.exit('Error: unknown file type "%s"' % file_to_upload)

        if wf_short_name == 'sanger-wxs':
            if 'ASCAT' in variant_type_to_data_type_etc['timings-supplement'][2]:
                variant_type_to_data_type_etc['timings-supplement'][2].remove('ASCAT')
            if 'BRASS' in variant_type_to_data_type_etc['timings-supplement'][2]:
                variant_type_to_data_type_etc['timings-supplement'][2].remove('BRASS')

    elif wf_short_name in (['gatk-mutect2']):
        fname_sample_part = metadata['samples'][0]['sampleId']
        if file_to_upload.endswith('mutect2-snv.vcf.gz') or file_to_upload.endswith('mutect2-snv.vcf.gz.tbi'):
            variant_type = 'snv'
        elif file_to_upload.endswith('mutect2-indel.vcf.gz') or file_to_upload.endswith('mutect2-indel.vcf.gz.tbi'):
            variant_type = 'indel'
        elif file_to_upload.endswith('_metrics.tgz'):
            variant_type = file_to_upload.split(".")[-2]
            if re.match(r'.+?\.normal.contamination_metrics.tgz', file_to_upload):
                fname_sample_part = normal_analysis['samples'][0]['sampleId']
        else:
            sys.exit('Error: unknown file type "%s"' % file_to_upload)

    elif wf_short_name in (['HaplotypeCaller']):
        sys.exit('Error: not implemented yet for "%s"' % wf_short_name)

    else:
        sys.exit('Error: unknown variant calling workflow "%s"' % wf_short_name)

    # file naming patterns:
    #   pattern:  <argo_sample_id_tumour>.[wgs|wxs].<date>.<wf_short_name>.[somatic|germline].[snv|indel|cnv|sv].vcf.gz
    #   example: TEST-PR.DO250183.SA610229.wxs.20200319.sanger-wxs.somatic.snv.vcf.gz
    new_fname = '.'.join([
                            metadata['studyId'],
                            metadata['samples'][0]['donor']['donorId'],
                            fname_sample_part,
                            experimental_strategy,
                            date_str,
                            wf_short_name,
                            somatic_or_germline.lower(),
                            variant_type,
                            'vcf.gz' if variant_type in ['snv', 'indel', 'cnv', 'sv'] else 'tgz'
                        ] + (['tbi'] if file_to_upload.endswith('.tbi') else []))

    file_info['fileName'] = new_fname
    extra_info = {}
    if new_fname.endswith('.vcf.gz'):
        file_info['dataType'] = variant_type_to_data_type_etc[variant_type][1]
    elif new_fname.endswith('.vcf.gz.tbi'):
        file_info['dataType'] = 'VCF Index'
    elif new_fname.endswith('.tgz'):
        if new_fname.endswith('-supplement.tgz'):
            file_info['dataType'] = variant_type_to_data_type_etc[variant_type][1]
        elif new_fname.endswith('_metrics.tgz'):
            file_info['dataType'] = variant_type_to_data_type_etc[variant_type][1]
        else:
            sys.exit('Error: unknown file type "%s"' % file_to_upload)

        tar = tarfile.open(file_to_upload)
        for member in tar.getmembers():
            if member.name.endswith('.extra_info.json'):
                f = tar.extractfile(member)
                extra_info = json.load(f)
                break
    else:
        sys.exit('Error: unknown file type "%s"' % file_to_upload)

    file_info['info'] = {
        'data_category': variant_type_to_data_type_etc[variant_type][0]
    }

    if wf_short_name in (['sanger-wgs', 'sanger-wxs']):
        file_info['info']['analysis_tools'] = variant_type_to_data_type_etc[variant_type][2]
    elif wf_short_name in (['gatk-mutect2']):
        file_info['info']['analysis_tools'] = variant_type_to_data_type_etc[variant_type][3]

    if extra_info:
        file_info['info'].update(extra_info)

    new_dir = 'out'
    try:
        os.mkdir(new_dir)
    except FileExistsError:
        pass

    dst = os.path.join(os.getcwd(), new_dir, new_fname)
    os.symlink(os.path.abspath(file_to_upload), dst)

    return file_info


def get_sample_info(sample_list):
    samples = copy.deepcopy(sample_list)
    for sample in samples:
        for item in ['info', 'sampleId', 'specimenId', 'donorId', 'studyId']:
            sample.pop(item, None)
            sample['specimen'].pop(item, None)
            sample['donor'].pop(item, None)

    return samples


def main(args):
    normal_analysis = {}
    with open(args.normal_analysis, 'r') as f:
        normal_analysis = json.load(f)

    tumour_analysis = {}
    if args.tumour_analysis:
        with open(args.tumour_analysis, 'r') as f:
            tumour_analysis = json.load(f)

    somatic_or_germline = 'Somatic'   # default
    if args.wf_short_name in ['sanger-wgs', 'sanger-wxs', 'gatk-mutect2']:
        if not tumour_analysis:
            sys.exit('Error: metadata for tumour is missing!')
    elif args.wf_short_name in ['HaplotypeCaller']:
        somatic_or_germline = 'Germline'
    else:
        sys.exit("Unsupported variant caller: %s" % args.wf_short_name)

    payload = {
        'analysisType': {
            'name': None
        },
        'studyId': normal_analysis.get('studyId'),  # normal/tumour analysis should always from the same study
        'experiment': {},
        'samples': [],
        'files': [],
        'workflow': {
            'workflow_name': workflow_full_name[args.wf_name],
            'workflow_short_name': args.wf_short_name,
            'workflow_version': args.wf_version,
            'run_id': args.wf_run,
            'session_id': args.wf_session,
            'inputs': [],
            'genome_build': 'GRCh38_hla_decoy_ebv'
        }
    }

    # get sample of the payload
    if somatic_or_germline == 'Somatic':  # somatic variants
        payload['samples'] = get_sample_info(tumour_analysis.get('samples'))
        payload['workflow']['inputs'] = [
            {
                "tumour_analysis_id": tumour_analysis.get("analysisId"),
                "analysis_type": "sequencing_alignment"
            },
            {
                "normal_analysis_id": normal_analysis.get("analysisId"),
                "analysis_type": "sequencing_alignment"
            }
        ]
        payload['experiment'] = {
            'experimental_strategy': tumour_analysis['experiment']['experimental_strategy'] if 'experimental_strategy' in tumour_analysis['experiment'] else tumour_analysis['experiment']['library_strategy'],
            'platform': tumour_analysis['experiment']['platform']
        }
    else:   # germline variants
        payload['samples'] = get_sample_info(normal_analysis.get('samples'))
        payload['workflow']['inputs'] = [
            {
                "normal_analysis_id": normal_analysis.get("analysisId"),
                "analysis_type": "sequencing_alignment"
            }
        ]
        payload['experiment'] = {
            'experimental_strategy': normal_analysis['experiment']['experimental_strategy'] if 'experimental_strategy' in normal_analysis['experiment'] else normal_analysis['experiment']['library_strategy'],
            'platform': normal_analysis['experiment']['platform']
        }

    analysis_type = 'variant_calling'
    for f in args.files_to_upload:
        if f.endswith('-supplement.tgz'): analysis_type = 'variant_calling_supplement'
        if f.endswith('_metrics.tgz'): analysis_type = 'qc_metrics'

        file_info = get_files_info(f, args.wf_short_name, args.wf_version, somatic_or_germline, normal_analysis, tumour_analysis)

        payload['files'].append(file_info)

    payload['analysisType']['name'] = analysis_type

    if not analysis_type == "qc_metrics":
        payload['variant_class'] = somatic_or_germline

    with open("%s.%s.payload.json" % (str(uuid.uuid4()), analysis_type), 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-n", dest="normal_analysis", required=True,
                        help="json file containing sequencing_alignment SONG analysis for normal sample")
    parser.add_argument("-t", dest="tumour_analysis", required=False,
                        help="json file containing sequencing_alignment SONG analysis for tumour sample")
    parser.add_argument("-f", dest="files_to_upload", type=str, nargs="+", help="Files to be uploaded", required=True)
    parser.add_argument("-w", dest="wf_name", type=str, help="workflow full name", required=True)
    parser.add_argument("-s", dest="wf_short_name", type=str, help="workflow short name", required=True)
    parser.add_argument("-v", dest="wf_version", type=str, required=True, help="workflow version")
    parser.add_argument("-r", dest="wf_run", type=str, required=True, help="workflow run ID")
    parser.add_argument("-j", dest="wf_session", type=str, required=True, help="workflow session ID")
    args = parser.parse_args()

    main(args)
