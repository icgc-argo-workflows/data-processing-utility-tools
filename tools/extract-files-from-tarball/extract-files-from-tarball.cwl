cwlVersion: v1.1
class: CommandLineTool
id: extract-files-from-tarball
requirements:
- class: InlineJavascriptRequirement
- class: ShellCommandRequirement
- class: NetworkAccess
  networkAccess: true

baseCommand: [ tar ]

inputs:
  tarball:
    type: File
    inputBinding:
      prefix: -xzf
      position: 0

  pattern:
    type: string

outputs:
  output_files:
    type: File[]
    secondaryFiles: ['.bai', '.crai', '.tbi', '.idx', 'md5']
    outputBinding:
      glob: ['*$(inputs.pattern)', '*$(inputs.pattern).bam', '*$(inputs.pattern).cram', '*$(inputs.pattern).vcf.gz']
