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

params.endpoint_url = "https://object.cancercollaboratory.org:9080"
params.bucket_name = "argo-test"
params.payload_json = "data/dna_alignment.test.json"
params.s3_credential_file = "/Users/junjun/credentials"


include "../s3-download"

workflow {
  main:
    s3Download(
      params.endpoint_url,
      params.bucket_name,
      file(params.payload_json),
      file(params.s3_credential_file)
    )

  publish:
    s3Download.out.download_file to: 'outdir', mode: 'copy', overwrite: true
    s3Download.out[1] to: 'outdir', mode: 'copy', overwrite: true
}
