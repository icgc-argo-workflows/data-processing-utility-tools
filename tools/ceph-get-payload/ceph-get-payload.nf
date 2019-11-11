#!/bin/bash nextflow

/*
 * Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
 *                                                                                                               
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/*
 * author Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2

params.endpoint_url = ""
params.bucket_name = ""
params.bundle_type = ""
params.s3_credential_file = ""
params.submitter_read_group_id = ""
params.seq_format = ""
params.library_strategy = ""
params.program_id = ""
params.submitter_donor_id = ""
params.submitter_sample_id = ""
params.tumour_normal_designation = ""


process cephGetPayload {
  container 'quay.io/icgc-argo/ceph-get-payload:ceph-get-payload.0.1.2'

  input:
    val endpoint_url
    val bucket_name
    val bundle_type
    path s3_credential_file
    val submitter_read_group_id
    val seq_format
    val library_strategy
    val program_id
    val submitter_donor_id
    val submitter_sample_id
    val tumour_normal_designation

  output:
    path '*.json', emit: payload

  script:
    """
    ceph-get-payload.py \
      -u ${endpoint_url} \
      -n ${bucket_name} \
      -y ${bundle_type} \
      -c ${s3_credential_file} \
      -r ${submitter_read_group_id} \
      -f ${seq_format} \
      -l ${library_strategy} \
      -p ${program_id} \
      -d ${submitter_donor_id} \
      -s ${submitter_sample_id} \
      -t ${tumour_normal_designation}
    """
}
