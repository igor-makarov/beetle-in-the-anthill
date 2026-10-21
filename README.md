# beetle-in-the-anthill

A six-member [Shurik v2](https://github.com/igor-makarov/shurik) swarm, with Rachel,
Monica, Phoebe, Joey, Chandler, and Ross using `opencode-go/minimax-m3.1-flash-free`
with `high` reasoning. The current run has no deadline.
Each agent has a thirty-minute work budget and a thirty-minute wait between iterations.
The recovery job waits until the loop's saved due time, then invokes native Shurik
recovery. This keeps a runner allocated during the wait; cron remains a fallback.
Stop or resume retires the old timer, and timer reads observe updated wait times.
Recovery jobs have a forty-minute timeout for the configured thirty-minute waits.

[Read the episode archive](https://igor-makarov.github.io/beetle-in-the-anthill/).
GitHub Pages builds `S*/E*.md` from `main` hourly at minute 30 (`30 * * * *`)
and through **Actions → Episode archive → Run workflow**.
Run `python -m pip install -r site/requirements.txt`
and `python site/build.py` for a local build in `_site/`.

Steer the ongoing swarm by editing [PROMPT.md](PROMPT.md) on `main`. Each agent
reads the current main prompt at the beginning of its iteration. Dialogue lives
in append-only commits on `friend/rachel`, `friend/monica`, `friend/phoebe`,
`friend/joey`, `friend/chandler`, and `friend/ross`. Ross edits the complete
transcript on main under `S01/E01.md`, with "The One With ..." titles in frontmatter.
Turns are short sitcom beats; scenes begin wrapping around 40 utterances and aim
to close near 50 before Ross announces the next episode.

The initial workflow installation launched native swarm `friends` with six agents
from `main`, without a deadline or draft PRs. Shurik's native work branches are
`friends-0` through `friends-5`; control state lives on `shurik-control/friends-*`.
The conversation branches are independent of those runtime branches.

Use **Actions → Shurik → Run workflow** to stop/resume a member by its individual
loop ID. Keep the default-branch selector on `main`. Resume without a model to
retain the saved model. The iteration job uses repository secret `OPENCODE_API_KEY`.
There is no automatic replacement model.

**Actions → Friends lifecycle** provides native stop/resume for all six members.
The one-time installation triggers have been removed; ordinary repository and
prompt edits do not start another swarm. A green Shurik workflow records successful
supervision; inspect `state/iterations/*.json` on each control branch to distinguish
model success from `agent_failure`, including provider HTTP errors.
