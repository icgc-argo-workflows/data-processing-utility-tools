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

params.endpoint_url = "s"
params.bucket_name = "b"
params.payload_json = "p"
params.s3_credential_file = "c"

process s3Download {
  container "quay.io/icgc-argo/s3-download:s3-download.0.1.2"

  input:
    val endpoint_url
    val bucket_name
    path payload_json
    path s3_credential_file

  output:
    path "*.{bam,cram,vcf.gz}", emit: download_file
    path "*.{bam.bai,cram.crai,vcf.gz.tbi}" optional true

  script:
    """
    s3-download.py \
      -s ${endpoint_url} \
      -b ${bucket_name} \
      -p ${payload_json} \
      -c ${s3_credential_file}
    """
}
