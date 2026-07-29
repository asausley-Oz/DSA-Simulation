# Planning Center → CareHub visit requests

Pulls a set of people out of your Planning Center account and turns them into
CareHub visit requests.

The Planning Center half is fully automated through their official API. The
CareHub half is a hand-off: CareHub (volunteeru.org) publishes no API, so by
default this tool produces an **import-ready CSV** and a **printable
worksheet**, and you create the requests in CareHub while logged in as
yourself. If you later get an authorized import endpoint, there's an opt-in
adapter to post directly (see "Direct submission" below).

## Setup

```bash
cd carehub_sync
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then fill in PCO_APP_ID / PCO_SECRET
```

Get a Planning Center **Personal Access Token** at
<https://api.planningcenteronline.com/oauth/applications> (the "Personal Access
Tokens" section). It's an Application ID + Secret pair; read access to People is
all this needs. Put them in `.env` as `PCO_APP_ID` and `PCO_SECRET`.

## Usage

### Quickest path: just give it names

For a handful of people, skip Lists entirely and name them directly. A starter
`people.txt` is included:

```bash
python -m planning_center_carehub.cli sync --names-file people.txt --dry-run
```

Or inline:

```bash
python -m planning_center_carehub.cli sync \
  --name "Denny Litton" --name "Robin Clendenning"
```

Each name is looked up in Planning Center. A name that matches exactly one
person is used. A name that matches nobody, or several people, is **reported
and skipped** — the tool never guesses which person you meant. When that
happens you'll see the candidates with their Planning Center ids, and you can
re-run with a fuller name.

### From a Planning Center List

Find the Planning Center List you want to sync from:

```bash
python -m planning_center_carehub.cli lists
```

Preview what would be created (touches nothing):

```bash
python -m planning_center_carehub.cli sync --source list --list-id 123456 --dry-run
```

Generate the CSV + worksheet:

```bash
python -m planning_center_carehub.cli sync --source list --list-id 123456
```

Output lands in `output/`:

- `carehub_visit_requests.csv` — one row per visit request, ready to import or
  paste
- `carehub_visit_requests.md` — a checklist with each person's contact details,
  for entering by hand
- `sync_state.json` — remembers who's already been submitted

You can also pull everyone instead of a list:

```bash
python -m planning_center_carehub.cli sync --source all --status active
```

## Re-running is safe

Each run compares against `output/sync_state.json` and only emits people who are
**new** or whose **contact details changed**. Running twice in a row produces
nothing the second time, so you won't create duplicate visit requests. Delete
the state file to force a full re-emit.

## Configuring the fields

`planning_center_carehub/transform.py` is the single place that decides what a
visit request looks like — request type, priority, and the note wording. Edit
`to_visit_request()` there if your CareHub form uses different labels.

Defaults for type and priority can also be set in `.env`
(`VISIT_REQUEST_TYPE`, `VISIT_PRIORITY`).

## Direct submission (opt-in, advanced)

`HttpCareHubClient` in `planning_center_carehub/carehub.py` can POST requests
directly, but it ships unwired on purpose. To use it you need to supply:

- `CAREHUB_SUBMIT_URL` — an endpoint you're authorized to call
- `CAREHUB_AUTH_HEADER` — your own session's authorization value
- a payload mapping in `HttpCareHubClient.build_payload()` matching what
  CareHub actually expects

Set `CAREHUB_SUBMIT_URL` and the CLI switches from files to direct posting.
Leave it blank and it stays on the safe file path. Since you're a regular
CareHub user rather than its operator, the right way to get this is to ask
CareHub's team for an import path or API access rather than scripting against
their site.

## Tests

```bash
cd carehub_sync
python -m pytest tests -q
```

Tests cover the Planning Center JSON:API parsing (including people with missing
contact info and multiple emails), the person → visit request mapping, the
duplicate-suppression state machine, and the CSV/worksheet output. They use
fixture data, so no network or credentials are needed.
