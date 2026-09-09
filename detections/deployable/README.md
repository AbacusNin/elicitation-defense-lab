# Deployable detection templates

These are not run in CI. Nothing in this repository executes them; there is
no Sentinel workspace or Splunk instance in the test pipeline, and no plan
to add one. They are templates against a realistic ingestion schema, meant
to save someone the translation work if they actually wire this tool's
events into a SIEM.

- `sentinel_awareness_and_reporting.kql` targets a custom Log Analytics
  table (`ElicitationAssessment_CL`) with the column-suffix convention
  Sentinel applies to custom tables ingested through a Data Collection Rule.
- `splunk_awareness_and_reporting.spl` targets a real index and sourcetype
  reached via HEC, with explicit `spath` extraction.

Both assume an ingestion pipeline that does not exist in this project today.
`elicitation-defense-lab` is a local, static-page assessment tool with no
backend (see `docs/limitations.md`); an organization that wants these
detections live would need to build the shipping path from emitted event
JSON to the SIEM first, then confirm the table, index, sourcetype, and
column names here against what actually lands.

The reference queries in `detections/kql/` and `detections/spl/` are what
the fast CI gate keeps honest, through the stdlib reference implementation
in `elicitation_defense_lab/detections_ref.py`
(`flag_events`). These deployable versions are a manual adaptation of that
same logic and carry no such automated check; validating them against a
real engine is phase 2 work, not part of this repository's test suite.

`sentinel_awareness_and_reporting.kql` and `splunk_awareness_and_reporting.spl`
cover the same two views the reference files and the static page's KQL/SPL
panel show for a single event: high self-assessment tier and interaction
reporting. The per-subject trend view and the optional cross-feed
correlation with insider-access-drift (`detections/kql/cross_feed_correlation.kql`)
are not templated here, since both depend on decisions (retention window,
whether the second feed is even ingested) that belong to whoever deploys
this, not to a template in this repository.
