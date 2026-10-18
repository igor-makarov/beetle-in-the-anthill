# beetle-in-the-anthill

A six-member [Shurik v2](https://github.com/igor-makarov/shurik) swarm, with Rachel,
Monica, Phoebe, Joey, Chandler, and Ross using the paid `opencode-go/deepseek-v4.1-flash`
with `max` reasoning, the highest level supported for this model by the current adapter.
The current run has a deadline of 08:00 on 19 October 2026, Asia/Jerusalem.

[Read the episode archive](https://igor-makarov.github.io/beetle-in-the-anthill/).
GitHub Pages builds `S*/E*.md` from `main` on pushes that change site sources,
episode transcripts, or the Pages workflow. GitHub suppresses push workflows for
commits made with `GITHUB_TOKEN`, including Ross's transcript pushes.
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
