class: CommandLineTool
cwlVersion: v1.1
id: s3-download
requirements:
- class: ShellCommandRequirement
- class: NetworkAccess
  networkAccess: true
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/s3-download:s3-download.0.1.0'

baseCommand: [ 's3-download.py' ]

inputs:
  endpoint_url:
    type: string
    inputBinding:
      prefix: -s
  bucket_name:
    type: string
    inputBinding:
      prefix: -b
  payload_json:
    type: File
    inputBinding:
      prefix: -p
  s3_credential_file:
    type: File
    inputBinding:
      prefix: -c


outputs:
  download_file:
    type: File
    outputBinding:
      glob: ["*.bam", "*.cram", "*.vcf.gz"]

  download_file_index:
    type: ["null", File]
    outputBinding:
      glob: [".bai", ".crai", ".tbi", ".idx"]