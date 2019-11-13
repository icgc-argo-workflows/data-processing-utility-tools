class: CommandLineTool
cwlVersion: v1.1
id: payload-generation

requirements:
- class: NetworkAccess
  networkAccess: true
- class: InlineJavascriptRequirement
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/payload-generation:payload-generation.0.1.5.1'

baseCommand: [ 'payload-generation.py' ]

inputs:
  bundle_type:
    type: string
    inputBinding:
      prefix: -t
  payload_schema_version:
    type: string
    inputBinding:
      prefix: -p
  user_submit_metadata:
    type: File?
    inputBinding:
      prefix: -m
  file_to_upload:
    type: File
    inputBinding:
      prefix: -f
    secondaryFiles: [.bai?, .crai?, .tbi?, .idx?]
  analysis_input_payload:
    type: File[]?
    inputBinding:
      prefix: -a
  wf_short_name:
    type: string?
    inputBinding:
      prefix: -c
  wf_version:
    type: string?
    inputBinding:
      prefix: -v


outputs:
  payload:
    type: File
    outputBinding:
      glob: '$(inputs.bundle_type).*.json'

  variant_call_renamed_result:
    type: ["null", File]
    secondaryFiles: [ ".tbi?", ".idx?" ]
    outputBinding:
      glob: '*.$(inputs.wf_short_name).$(inputs.wf_version).somatic.*.vcf.gz'



