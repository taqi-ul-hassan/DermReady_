# Data and privacy plan

SCIN access and the current official license have been reviewed; see docs/SCIN_USAGE.md. Read the current official terms before use. The MIT code license does not cover SCIN or pretrained model artifacts.

Do not attempt to identify or link dataset contributors. Preserve label provenance locally.
Do not publish images or case-level metadata merely because they are available for research.
Keep datasets, manifests, split artifacts, checkpoints, and private uploads out of Git.
Review aggregate reports and notebook outputs before committing; remove embedded images and sensitive records.

The local app does not add uploads to its dataset or image logs. Gradio creates temporary uploads and previews: cleanup checks every 30 seconds for files older than 60 seconds. This is not instant deletion; browser and hosting caches may persist. Clear resets the displayed result. Analytics, run history, public sharing and flagging are disabled, and the server binds to localhost by default. Private data and checkpoint paths are blocked from HTTP serving. See RUN_APP.md for handling and limits.

The optional preparation checklist is self-reporting within the app session; it never changes model decisions. The installation checker reports software readiness and artifact identity without reading medical images or case records. Public hosting requires a separate review of access controls, logs, caches, retention and visibility.
Use only explicitly permitted public examples and record their attribution.

