class: CommandLineTool
cwlVersion: v1.1
id: ceph-get-payload
requirements:
- class: ShellCommandRequirement
- class: NetworkAccess
  networkAccess: true
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/ceph-get-payload:ceph-get-payload.0.1.2'

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
  submitter_read_group_id:
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
  program_id:
    type: string
    inputBinding:
      prefix: -p
  submitter_donor_id:
    type: string
    inputBinding:
      prefix: -d
  submitter_sample_id:
    type: string
    inputBinding:
      prefix: -s
  tumour_normal_designation:
    type: string
    inputBinding:
      prefix: -t


outputs:
  payload:
    type: File
    outputBinding:
      glob: ['*.json']
