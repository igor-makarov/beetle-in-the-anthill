const { execFileSync } = require('node:child_process');
const { appendFileSync } = require('node:fs');

function waitState(control, expected, now) {
  if (control.id !== expected.id || control.generation !== expected.generation ||
      control.next !== expected.iteration + 1 || control.status !== 'running' ||
      control.owner || !control.nextRunAt) return { kind: 'skip' };

  const due = Date.parse(control.nextRunAt);
  const deadline = control.deadline ? Date.parse(control.deadline) : Infinity;
  if (!Number.isFinite(due) || Number.isNaN(deadline)) throw new Error('Invalid loop timing');
  if (now >= deadline) return { kind: 'skip' };
  if (now >= due) return { kind: 'ready' };
  return { kind: 'wait', until: Math.min(due, deadline) };
}

async function waitForNextIteration({ readControl, expected, now = Date.now,
  sleep = ms => new Promise(resolve => setTimeout(resolve, ms)), report = console.log }) {
  let errors = 0;
  let lastDue;
  for (;;) {
    let control;
    try {
      control = await readControl();
      errors = 0;
    } catch (error) {
      if (++errors >= 5) throw new Error('Cannot read loop control after five attempts', { cause: error });
      report('Control read failed; retrying in one minute.');
      await sleep(60_000);
      continue;
    }
    const decision = waitState(control, expected, now());
    if (decision.kind !== 'wait') return decision.kind === 'ready';
    if (lastDue !== decision.until) {
      report(`Waiting for ${expected.id} until ${new Date(decision.until).toISOString()}`);
      lastDue = decision.until;
    }
    await sleep(Math.max(1, Math.min(60_000, decision.until - now())));
  }
}

function readControl(repo, id, request = execFileSync) {
  const path = `repos/${repo}/contents/control.json?ref=${encodeURIComponent(`shurik-control/${id}`)}`;
  const response = JSON.parse(request('gh', ['api', path], {
    encoding: 'utf8', timeout: 30_000, stdio: ['ignore', 'pipe', 'pipe'],
  }));
  if (response.encoding !== 'base64' || typeof response.content !== 'string') {
    throw new Error('Expected a control JSON file');
  }
  return JSON.parse(Buffer.from(response.content, 'base64').toString('utf8'));
}

async function main() {
  const expected = { id: process.env.SHURIK_WAIT_LOOP_ID,
    generation: Number(process.env.SHURIK_WAIT_GENERATION),
    iteration: Number(process.env.SHURIK_WAIT_ITERATION) };
  if (!expected.id || !Number.isSafeInteger(expected.generation) || expected.generation < 1 ||
      !Number.isSafeInteger(expected.iteration) || expected.iteration < 1) {
    throw new Error('Expected an iteration loop ID, generation, and sequence');
  }
  const ready = await waitForNextIteration({ expected,
    readControl: () => readControl(process.env.GH_REPO, expected.id) });
  appendFileSync(process.env.GITHUB_OUTPUT, `ready=${ready}\n`);
  console.log(ready ? 'Saved wait has elapsed; invoking native recovery.' : 'Wait no longer belongs to this iteration.');
}

module.exports = { waitState, waitForNextIteration, readControl };
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
