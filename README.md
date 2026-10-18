# beetle-in-the-anthill

A six-member [Shurik v2](https://github.com/igor-makarov/shurik) swarm, with Rachel,
Monica, Phoebe, Joey, Chandler, and Ross using `opencode/beam-free` with high reasoning.

[Read the episode archive](https://igor-makarov.github.io/beetle-in-the-anthill/).
GitHub Pages builds `S*/E*.md` from `main` every five minutes and on source pushes.
GitHub may delay scheduled builds. Run `python -m pip install -r site/requirements.txt`
and `python site/build.py` for a local build in `_site/`.

Steer the ongoing swarm by editing [PROMPT.md](PROMPT.md) on `main`. Each agent
reads the current main prompt at the beginning of its iteration. Dialogue lives
in append-only commits on `friend/rachel`, `friend/monica`, `friend/phoebe`,
`friend/joey`, `friend/chandler`, and `friend/ross`. Ross edits the complete
transcript on main under `S01/E01.md`, with "The One With ..." titles in frontmatter.

The initial workflow installation launches native swarm `friends` with six agents
from `main`, without a deadline or draft PRs. Shurik's native work branches are
`friends-0` through `friends-5`; control state lives on `shurik-control/friends-*`.
The conversation branches are independent of those runtime branches.

Use **Actions → Shurik → Run workflow** to stop/resume a member by its individual
loop ID. Keep the default-branch selector on `main`. Resume without a model to
retain the saved model. The iteration job uses repository secret `OPENCODE_API_KEY`.
There is no automatic replacement model.
