class: CommandLineTool
cwlVersion: v1.1
id: get-payload
requirements:
- class: ShellCommandRequirement
- class: NetworkAccess
  networkAccess: true
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/get-payload:get-payload.0.1.0'

baseCommand: [ 'ceph-get-payload.py' ]

inputs:
  endpoint_url:
    type: string
    inputBinding:
      prefix: -u
  bucket_name:
    type: string
    inputBinding:
      prefix: -n
  bundle_type:
    type: string
    inputBinding:
      prefix: -y
  s3_credential_file:
    type: File
    inputBinding:
      prefix: -c
  read_group_submitter_id:
    type: string?
    inputBinding:
      prefix: -r
  seq_format:
    type: string?
    inputBinding:
      prefix: -f
  library_strategy:
    type: string
    inputBinding:
      prefix: -l
  program:
    type: string
    inputBinding:
      prefix: -p
  donor_submitter_id:
    type: string
    inputBinding:
      prefix: -d
  sample_submitter_id:
    type: string
    inputBinding:
      prefix: -s
  specimen_type:
    type: string
    inputBinding:
      prefix: -t


outputs:
  payload:
    type: File
    outputBinding:
      glob: ['*.json']
