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
params.bundle_type = "sequencing_experiment"
params.s3_credential_file = "/Users/junjun/credentials"
params.submitter_read_group_id = ""
params.seq_format = ""
params.library_strategy = "WXS"
params.program_id = "BRCA-UK"
params.submitter_donor_id = "CGP_donor_1069291"
params.submitter_sample_id = "PD3890a"
params.tumour_normal_designation = "Primary tumour"

include '../ceph-get-payload' params(params)


workflow {
  main:
    cephGetPayload(
      params.endpoint_url,
      params.bucket_name,
      params.bundle_type,
      file(params.s3_credential_file),
      params.submitter_read_group_id,
      params.seq_format,
      params.library_strategy,
      params.program_id,
      params.submitter_donor_id,
      params.submitter_sample_id,
      params.tumour_normal_designation
    )
  publish:
    cephGetPayload.out.payload to: 'outdir', mode: 'copy', overwrite: true
}
