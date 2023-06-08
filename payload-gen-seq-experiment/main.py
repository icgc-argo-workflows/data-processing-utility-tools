#!/usr/bin/env python3


"""
 Copyright (c) 2019-2021, Ontario Institute for Cancer Research (OICR).

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
   Edmund Su <edmund.su@oicr.on.ca>
 """

import sys
import uuid
import json
import csv
import textwrap
import argparse
import requests
import re
import jsonschema
import os
import hashlib


TSV_FIELDS = {}

TSV_FIELDS['experiment'] = {}
TSV_FIELDS['experiment']['core']=[
    'type', 'program_id', 'submitter_sequencing_experiment_id', 'submitter_donor_id', 'gender',
    'submitter_specimen_id', 'tumour_normal_designation', 'specimen_type', 'specimen_tissue_source',
    'submitter_sample_id','sample_type', 'submitter_matched_normal_sample_id', 'sequencing_center', 
    'platform', 'platform_model','experimental_strategy', 'sequencing_date', 'read_group_count']
TSV_FIELDS['experiment']["conditional"]=[
    "library_preparation_kit",
    "library_strandedness",
    "rin","dv200",
    "target_capture_kit","number_of_genes","gene_padding","coverage",
    "primary_target_regions","capture_target_regions"
    ]

TSV_FIELDS['read_group']= {}
TSV_FIELDS['read_group']["core"]=[
    'type', 'submitter_read_group_id', 'read_group_id_in_bam', 'submitter_sequencing_experiment_id', 'platform_unit',
    'is_paired_end', 'file_r1', 'file_r2', 'read_length_r1', 'read_length_r2', 'insert_size', 'sample_barcode', 'library_name'
    ]
TSV_FIELDS['read_group']["conditional"]=[]

EGA_FIELDS={
    "ega_file_id":"EGAF",
    "ega_dataset_id":"EGAD",
    "ega_experiment_id":"EGAX",
    "ega_sample_id":"EGAN",
    "ega_study_id":"EGAS",
    "ega_run_id":"EGAR",
    "ega_policy_id":"EGAP",
    "ega_analysis_id":"EGAZ",
    "ega_submission_id":"EGAB",
    "ega_dac_id":"EGAC"
}

TSV_FIELDS['file']={}
TSV_FIELDS['file']["core"]=['type', 'name', 'size', 'md5sum', 'path', 'format']
TSV_FIELDS['file']["conditional"]=list(EGA_FIELDS.keys())


def empty_str_to_null(metadata):
    for k in metadata:
        if k in ['read_groups', 'files','experiment']:
            for i in range(len(metadata[k])):
                empty_str_to_null(metadata[k][i])
        if isinstance(metadata[k], str) and metadata[k] in ["", "_NULL_","null","NULL","Null","None","NONE","none"]:
            metadata[k] = None


def tsv_confomity_check(ftype, tsv):
    core_fields = TSV_FIELDS[ftype]['core']
    conditional_fields = TSV_FIELDS[ftype]['conditional']
    expected_fields=core_fields+conditional_fields

    header_processed = False
    with open(tsv, 'r') as t:
        uniq_row = {}
        for l in t:
            l = l.rstrip('\n').rstrip('\r')  # remove trailing newline, remove windows `\r` (just in case)
            if not header_processed:  # it's header
                fields = l.split('\t')
                if len(fields) != len(set(fields)):
                    sys.exit("Error found: Field duplicated in input TSV: %s, offending header: %s\n" % (tsv, l))

                missed_fields = set(core_fields) - set(fields)
                if missed_fields:  # missing fields
                    sys.exit("Error found: Field missing in input TSV: %s, offending header: %s. Missed field(s): %s\n" % \
                        (tsv, l, ', '.join(missed_fields)))

                unexpected_fields = set(fields) - set(expected_fields)
                if unexpected_fields:  # unexpected fields
                    sys.exit("Error found: Unexpected field in input TSV: %s, offending header: %s. Unexpected field(s): %s\n" % \
                        (tsv, l, ', '.join(unexpected_fields)))

                header_processed = True

            else:  # it's data row
                # at this point we only check whether number of values matches number of expected fields and uniqueness check,
                # later steps will perform more sophisticated content check
                values = l.split('\t')
                if len(values) < len(core_fields):
                    sys.exit("Error found: number of fields: %s does not match expected: %s, offending data row: %s\n" % \
                        (len(values), len(expected_fields), l))

                if l in uniq_row:
                    sys.exit("Error found: data row repeated in file: %s, offending data row: %s\n" % (tsv, l))
                else:
                    uniq_row[l] = True


def load_all_tsvs(exp_tsv, rg_tsv, file_tsv):
    metadata_dict = {}
    with open(exp_tsv, 'r') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
        if len(rows) != 1:
            sys.exit("Error found: experiment TSV expects exactly one data row, offending file: %s has %s row(s)\n" % \
                (exp_tsv, len(rows)))
        rows[0]['read_group_count'] = int(rows[0]['read_group_count'])
        metadata_dict.update(rows[0])

    with open(rg_tsv, 'r') as f:
        metadata_dict['read_groups'] = []
        for rg in csv.DictReader(f, delimiter='\t'):
            if rg['is_paired_end'].lower() == 'true':
                rg['is_paired_end'] = True
            elif rg['is_paired_end'].lower() == 'false':
                rg['is_paired_end'] = False
            else:
                rg['is_paired_end'] = None

            for field in ('read_length_r1', 'read_length_r2', 'insert_size'):
                if isinstance(rg[field],str):
                    if re.match("^[0-9]+$", rg[field]):
                        rg[field] = int(rg[field])
                        continue
                    for empty_string in ["", "_NULL_",'null',"NULL","Null","None","NONE","none"]:
                        if rg[field]==empty_string:
                            rg[field] = None
                            break
                elif isinstance(rg[field],int):
                    rg[field] = int(rg[field])
                elif rg[field] is None:
                    rg[field] = None
                else:
                    sys.exit("Unrecognnized value '%s' in field %s for '%s'" % (str(rg[field]),field,rg['submitter_read_group_id']))

            metadata_dict['read_groups'].append(rg)

        if len(metadata_dict['read_groups']) == 0:
            sys.exit("Error found: read group TSV does not contain any read group information\n")

    with open(file_tsv, 'r') as f:
        metadata_dict['files'] = []
        for f in csv.DictReader(f, delimiter='\t'):
            if f['size']:
                f['size'] = int(f['size'])
            else:
                f['size'] = None

            metadata_dict['files'].append(f)

        if len(metadata_dict['files']) == 0:
            sys.exit("Error found: file TSV does not contain any file information\n")

    return metadata_dict


def validate_args(args):
    if args.metadata_json and \
            not (args.experiment_info_tsv and args.read_group_info_tsv and args.file_info_tsv):
        return True
    elif not args.metadata_json and \
            (args.experiment_info_tsv and args.read_group_info_tsv and args.file_info_tsv):
        return True
    else:
        sys.exit(textwrap.dedent(
            """
            Usage:
                When '-m' is provided, '-x','-r' and '-f' are ignored arguments can be used
                When '-m' is not provided, please provide all of these arguments: '-x', '-r' and '-f'
                Optionally '-s' a schema URL can be provided, which the payload will be validated against
            """
        ))

def validatePayload(payload,url):

    resp=requests.get(url)
    if not resp.status_code==200:
        sys.exit("Unable to retrieve schema. Please check URL\n")

    try:
        jsonschema.validate(instance=payload,schema=resp.json()['schema'])
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        sys.exit("Payload failed to validate against schema\n")
    else:
        return True
        
def calculate_size(file_path):
    return os.stat(file_path).st_size

def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()

def replace_cram_with_bam(payload,bam_from_cram,bam_from_cram_reference):
    for bam in bam_from_cram:
        for cram in payload['files']:
            if re.sub('\.cram$','',cram['fileName'])==re.sub('\.bam$','',bam) and cram['fileType']=='CRAM':
                cram['info']['original_cram_info']={}
                cram['info']['original_cram_info']['fileName']=cram['fileName']
                cram['info']['original_cram_info']['fileSize']=cram['fileSize']
                cram['info']['original_cram_info']['fileMd5sum']=cram['fileMd5sum']
                cram['info']['original_cram_info']['fileType']=cram['fileType']
                cram['info']['original_cram_info']['referenceFileName']=bam_from_cram_reference
                cram['fileName']=bam
                cram['fileSize']=calculate_size(bam)
                cram['fileMd5sum']=calculate_md5(bam)
                cram['fileType']="BAM"
        for rg in payload["read_groups"]:
            if re.sub('\.cram$','',rg['file_r1'])==re.sub('\.bam$','',bam):
                rg['file_r1']=bam
                if rg['is_paired_end']:
                    rg['file_r2']=bam
    return(payload)
    
def main(metadata,url,bam_from_cram,bam_from_cram_reference,recalculate_size_and_md5_files,extra_info=dict()):
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

    # optional experiment arguements
    # Strings
    optional_experimental_fields=TSV_FIELDS['experiment']["conditional"]
    optional_experimental_fields.remove("rin")

    for optional_experimental_field in optional_experimental_fields:
        if optional_experimental_field in metadata.keys():
            payload['experiment'][optional_experimental_field]=metadata.get(optional_experimental_field)
    # Int
    optional_experimental_fields=["rin"]
    for optional_experimental_field in optional_experimental_fields:
        if metadata.get(optional_experimental_field):
            payload['experiment'][optional_experimental_field]=int(metadata.get(optional_experimental_field))

    # RNA-seq library_Strandedness requirement check
    if metadata.get('experimental_strategy')=='RNA-Seq' and not metadata.get("library_strandedness"):
        sys.exit(f"'experimental_strategy' 'RNA-Seq' specified but 'library_strandedness' is missing. Resubmit with both values 'experimental_strategy' and 'library_strandedness'")

    # Targetted Sequencing :
    if metadata.get('experimental_strategy')=="Targeted-Seq" or metadata.get('experimental_strategy')=="WXS":
        for field in ['target_capture_kit','primary_target_regions','capture_target_regions']:
            if field not in metadata.keys():
                sys.exit(f"'experimental_strategy' '%s' specified but '%s' is missing. Resubmit with both values 'experimental_strategy' and '%s'" % (metadata.get('experimental_strategy'),field,field))

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
                'dataType': 'Submitted Reads',
                'info': {
                    'data_category': 'Sequencing Reads'
                }
            }
        )
        for optional_file_field in TSV_FIELDS['file']["conditional"]:
            if input_file.get(optional_file_field):
                if re.findall("^"+EGA_FIELDS[optional_file_field]+'[0-9]{1,32}$',input_file.get(optional_file_field)):
                    if payload['files'][-1]['info'].get("ega"):
                        payload['files'][-1]['info']['ega'][optional_file_field]=input_file.get(optional_file_field)
                    else:
                        payload['files'][-1]['info']['ega']={}
                        payload['files'][-1]['info']['ega'][optional_file_field]=input_file.get(optional_file_field)
                else:
                    sys.exit(f"Field '%s' in file '%s' with value '%s' does not match expected regex pattern '^%s[0-9]{1,32}$'" % (optional_file_field,input_file.get('name'),input_file.get(optional_file_field),EGA_FIELDS[optional_file_field]))

    for rg in metadata.get("read_groups"):
        if "type" in rg:
            rg.pop('type')  # remove 'type' field
        if "submitter_sequencing_experiment_id" in rg:
            rg.pop('submitter_sequencing_experiment_id')  # remove 'submitter_sequencing_experiment_id' field
        payload['read_groups'].append(rg)


    if extra_info:
        for item,dict_to_update,submitter_id in zip(
            ["sample","donor","specimen","experiment"],
            [payload['samples'][0],payload['samples'][0]['donor'],payload['samples'][0]['specimen'],payload['experiment']],
            ["submitterSampleId","submitterDonorId","submitterSpecimenId","submitter_sequencing_experiment_id"]
        ):
            if not item in extra_info:
                continue
            for key in extra_info[item][dict_to_update.get(submitter_id)].keys() :
                if key in dict_to_update:
                    sys.exit(f"Conflicting entries detected. Attempted altering of existing field {key} in {item}")
            if extra_info[item][dict_to_update.get(submitter_id)]:
                    dict_to_update.update(extra_info[item][dict_to_update.get(submitter_id)])

        for item,list_to_parse,unique_ele_name in zip(
            ["files","read_groups"],
            [payload["files"],payload['read_groups']],
            ["fileName","submitter_read_group_id"]
        ):
            if not item in extra_info:
                continue
            for ele_to_update in extra_info[item].keys():
                for existing_ele in list_to_parse:
                    if existing_ele[unique_ele_name]!=ele_to_update:
                        continue
                    for key in extra_info[item][ele_to_update].keys():
                        if key in existing_ele:
                            sys.exit(f"Conflicting entries detected. Attempted altering of existing field {key} in {existing_ele}")
                    if item=='files':
                        existing_ele['info'].update(extra_info[item][ele_to_update])
                    else:
                        existing_ele.update(extra_info[item][ele_to_update])
    if len(bam_from_cram)>0:
        payload=replace_cram_with_bam(payload,bam_from_cram,bam_from_cram_reference)

    if len(recalculate_size_and_md5_files)>=1:
        for recalculate in recalculate_size_and_md5_files:
            for file in payload['files']:
                if file['fileName']==recalculate:
                    file['fileMd5sum']=calculate_md5(recalculate)
                    file['fileSize']=calculate_size(recalculate)

    validatePayload(payload,url)
    with open("%s.sequencing_experiment.payload.json" % str(uuid.uuid4()), 'w') as f:
        f.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--metadata-json",
                        help="json file containing experiment, read_group and file information submitted from user")
    parser.add_argument("-x", "--experiment-info-tsv",
                        help="tsv file containing experiment information submitted from user")
    parser.add_argument("-r", "--read-group-info-tsv",
                        help="tsv file containing read_group information submitted from user")
    parser.add_argument("-f", "--file-info-tsv",
                        help="tsv file containing file information submitted from user")
    parser.add_argument("-e", "--extra-info-tsv",
                        help="tsv file containing additional information pertaining to existing experiment, read_group, and file information submitted from user that does not fit within existing schemas")
    parser.add_argument("-s", "--schema-url",
                        help="URL to validate schema against")
    parser.add_argument("-b", "--bam-from-cram",nargs="+",default=[],
                        help="BAM files that have converted from CRAM")
    parser.add_argument("-br", "--bam-from-cram-reference",default=None,
                        help="Name of reference file used in cram2bam conversion")
    parser.add_argument("-z", "--recalculate-size-and-md5-files",default=[],nargs="*",
                        help="Supplied files here will have their md5sum and size relcalculated")                        
    args = parser.parse_args()

    validate_args(args)

    if args.schema_url:
        url=args.schema_url
    else:
        url="https://submission-song.rdpc.cancercollaboratory.org/schemas/sequencing_experiment"

    if args.metadata_json:
        with open(args.metadata_json, 'r') as f:
            metadata = json.load(f)

        if len(args.bam_from_cram)>0:
            payload=replace_cram_with_bam(metadata,args.bam_from_cram,args.bam_from_cram_reference)
        validatePayload(metadata,url)
        with open("%s.sequencing_experiment.payload.json" % str(uuid.uuid4()), 'w') as f:
            f.write(json.dumps(metadata, indent=2))
    else:
        # firstly TSV format conformity check, if not well-formed no point to continue
        tsv_confomity_check('experiment', args.experiment_info_tsv)
        tsv_confomity_check('read_group', args.read_group_info_tsv)
        tsv_confomity_check('file', args.file_info_tsv)

        # all TSV are well-formed, let's load them
        metadata = load_all_tsvs(
                            args.experiment_info_tsv,
                            args.read_group_info_tsv,
                            args.file_info_tsv
                        )

        extra_info = dict()
        if args.extra_info_tsv:
            with open(args.extra_info_tsv, 'r') as f:
                for row in csv.DictReader(f, delimiter='\t'):
                
                    for row_type in ['type','submitter_id','submitter_field','field_value']:
                        if row_type not in row.keys():
                            sys.exit(f"Incorrect formatting of : {args.extra_info_tsv}. {row_type} is missing") 

                    row_type = row['type']
                    row_id= row['submitter_id']
                    row_field= row['submitter_field']
                    row_val= row['field_value']
        
                    if (row_type!="sample") and (row_type!="donor") and (row_type!="specimen") and (row_type!="files") and (row_type!="experiment"):
                        sys.exit(f"Incorrect identifier supplied. Must be on the following : 'sample','donor','specimen','files','experiments'. Offending value: {type}, in file: {args.extra_info_tsv}")
            
                    if row_type not in extra_info:
                        extra_info[row_type]=dict()
                    if row_id not in extra_info[row_type]:
                        extra_info[row_type][row_id]=dict()
                    extra_info[row_type][row_id][row_field]=row_val
                    

        main(metadata,url,args.bam_from_cram,args.bam_from_cram_reference,args.recalculate_size_and_md5_files,extra_info)
