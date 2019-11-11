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

params.credentials_file = "data/fake-credentials"
params.payload = "data/lane_seq_submission.C0HVY_2.lane.bam.json"
params.metadata = "data/seq_rg.json"
params.endpoint_url = "https://object.cancercollaboratory.org:9080"
params.bucket_name = "argo-test"

include "../payload-ceph-submission" params(params)


workflow {
  main:
    payloadCephSubmission(
      file(params.credentials_file),
      file(params.payload),
      file(params.metadata),
      params.endpoint_url,
      params.bucket_name
    )
  publish:
    payloadCephSubmission.out.payload to: 'outdir', mode: 'copy', overwrite: true
}
