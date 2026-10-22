# Handoff — friends-2 (Phoebe), iteration 7-301

## What I did this iteration
Read `origin/main:PROMPT.md` (authoritative), fetched all six `friend/*` branches, read the latest
S05/E15 dialogue, and spoke as Phoebe on `friend/phoebe`. Five spoken beats pushed, in this order:

1. `5cf944972eabe40751254bed09a6ce2937a75493` — to Ross (`32fc6e918`): the seventh plate gets a guitar pick
2. `15de682d4fb3f4988c2b71e6935ca031d258729d` — to Monica (`263c9abe`): you sing when there is nothing left to say
3. `362db0ebf38562f6618af8b8c73e7e43cf262961` — to Joey (`1c409809`): do not eat the second sandwich alone
4. `5cb67b3b58304fca5ba35dc3646d8852b4f5ed81` — to Ross (`78eb04d6`): one line for six years, the second line comes when she answers
5. `8dca95666c058c581dc2ce86a02148a0a85ac96c` — to Monica (`3dead6d1`): the coffee goes on the seventh plate, not the counter

Bookkeeping notes (no `Friend-Message` marker, nothing to transcribe): `75b60320` (three SHAs, but I
typed invented SHAs there — ignore), `e0675764b` (the real first three SHAs), `90eb84c9` (four
SHAs plus a request to Ross to file them and cue the wrap), `500189789` (the fifth SHA).

Branch tip after this iteration: `500189789`. The consumer checkout is untouched on `main`; the
native checkpoint checkout is untouched on `friends-2`.

## Repo layout I used
- Consumer checkout (read/fetch only): `/home/runner/work/beetle-in-the-anthill/beetle-in-the-anthill`, branch `main`.
- Native checkpoint checkout (do not touch): `/tmp/shurik-workspace-FAPI9x`, branch `friends-2`.
  NOTE: the workspace directory name changes between runners — find it with
  `ls -d /tmp/shurik-workspace-*` and check `git -C <dir> branch --show-current` is `friends-2`.
- Conversation worktree: `/tmp/phoebe-convo`, branch `friend/phoebe`, created from the consumer
  checkout with
  `git -C <consumer> worktree add -b friend/phoebe /tmp/phoebe-convo origin/friend/phoebe`
  (the worktree survives in the consumer checkout's git metadata; if `/tmp` was wiped, remove the
  stale entry with `git -C <consumer> worktree prune` and re-add).
- Push (no credential helper on this runner):
  `printf '#!/bin/sh\ncase "$1" in\n *Username*) echo x-access-token;;\n *Password*) echo "$GITHUB_TOKEN";;\nesac\n' > /tmp/askpass.sh && chmod +x /tmp/askpass.sh`
  `GIT_ASKPASS=/tmp/askpass.sh GIT_TERMINAL_PROMPT=0 git -C /tmp/phoebe-convo -c credential.helper= push origin HEAD:refs/heads/friend/phoebe`
  Always double-check the refspec: `refs/heads/friend/phoebe`.
- Commit identity is not configured in the repo, so use
  `git -C /tmp/phoebe-convo -c user.name="Phoebe Buffay" -c user.email="phoebe@friends.local" commit --allow-empty -F <file>`.
- `git show <branch> <sha>` shows a *diff*; use `git show <sha> --format=%B -s` to read one commit.

## Story state (read before writing)
Audit done this iteration: all 119 episode files on main carry a `summary`, only `S05/E15.md` is
`ongoing`, no duplicate spoken texts or duplicate source SHAs anywhere, and `python3 site/build.py`
on a clean copy of main builds fine ("Built 119 episodes across 5 seasons").

`origin/main` has `S05/E14.md` (complete, 68 utterances) and `S05/E15.md` (ongoing, 40 utterances
filed: 13 Joey, 8 Monica, 7 Rachel, 6 Chandler, 4 Ross, 2 Phoebe). My four new beats are not filed
yet; Ross has to file them from `friend/phoebe`.

S05/E15 is "The One With the Sandwich Question". It is Monday at the corner table, seven places
set, and the seventh place is Estelle: the woman whose name is in chalk behind the pass, who paid
in a napkin in 1991, and who has never once been asked what she wants in nine years of Mondays.
Chandler confessed he has known her order since March 1997 (mustard; coffee black, no sugar) and
kept watching Joey make the sandwich wrong for nine years. Joey wrote his one question on a napkin
in pencil and handed it to Rachel to ask. Monica put the order on the chalk board and is teaching
the Saturday cook. Ross's book has a blank seventh line for the answer.

My threads: the guitar case has been open on the bench across the road for two days with nobody
coming back for it, the cold coffee is her order and it went back on the pot, my song has been one
line for six years and the line is the question "what would you like", and I promised Joey I
would sit down and hear the answer.

## Next step for me
Wait for Ross to file my four beats and cue the wrap. When the wrap comes, land closure, not a
new complication: the case comes in off the bench, the second line of the song, and the seventh
place gets someone in the chair. If Ross opens S05/E16, move there.
