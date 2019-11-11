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
params.payload_jsons = ""
params.s3_credential_file = ""
params.upload_file = ""


process s3Upload {
  container "quay.io/icgc-argo/s3-upload:s3-upload.0.1.6.0"

  input:
    val endpoint_url
    val bucket_name
    val bundle_type
    path payload_json
    path s3_credential_file
    path upload_file

  script:
    """
    s3-upload.py \
      -s ${endpoint_url} \
      -b ${bucket_name} \
      -t ${bundle_type} \
      -p ${payload_json} \
      -c ${s3_credential_file} \
      -f ${upload_file}
    """
}
