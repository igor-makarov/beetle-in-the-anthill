const assert = require('node:assert/strict');
const test = require('node:test');
const { waitState, waitForNextIteration, readControl } = require('../.github/scripts/wait-for-shurik.cjs');

const expected = { id: 'friends-0', generation: 6, iteration: 183 };
const start = Date.parse('2026-10-19T07:00:00Z');
const due = start + 30 * 60_000;
const control = { id: 'friends-0', generation: 6, next: 184, status: 'running',
  owner: null, nextRunAt: new Date(due).toISOString(), deadline: null };

test('reads and decodes the control branch through an encoded API ref', () => {
  const result = readControl('igor-makarov/beetle-in-the-anthill', expected.id, (command, args) => {
    assert.equal(command, 'gh');
    assert.deepEqual(args, ['api', 'repos/igor-makarov/beetle-in-the-anthill/contents/control.json?ref=shurik-control%2Ffriends-0']);
    return JSON.stringify({ encoding: 'base64', content: Buffer.from(JSON.stringify(control)).toString('base64') });
  });
  assert.deepEqual(result, control);
});

test('recovers exactly at the saved due time, never before it', async () => {
  assert.deepEqual(waitState(control, expected, due - 1), { kind: 'wait', until: due });
  assert.deepEqual(waitState(control, expected, due), { kind: 'ready' });
  let time = start;
  const sleeps = [];
  const ready = await waitForNextIteration({ expected, readControl: () => control,
    now: () => time, sleep: async ms => { sleeps.push(ms); time += ms; }, report: () => {} });
  assert.equal(ready, true);
  assert.equal(time, due);
  assert.equal(sleeps.length, 30);
  assert.ok(sleeps.every(ms => ms <= 60_000));
});

test('a stop, resume, new iteration, or active successor retires the old timer', () => {
  for (const patch of [{ status: 'stopped' }, { status: 'deadline' }, { generation: 7 },
    { next: 185 }, { id: 'friends-1' }, { owner: { runId: 'new-worker' } }, { nextRunAt: null }]) {
    assert.deepEqual(waitState({ ...control, ...patch }, expected, due), { kind: 'skip' });
  }
});

test('observes a stop during the wait without requesting recovery', async () => {
  let time = start;
  const ready = await waitForNextIteration({ expected,
    readControl: () => ({ ...control, status: time === start ? 'running' : 'stopped' }),
    now: () => time, sleep: async ms => { time += ms; }, report: () => {} });
  assert.equal(ready, false);
  assert.equal(time, start + 60_000);
});

test('an edited due time takes effect on the next read', async () => {
  let time = start;
  const changedDue = start + 90_000;
  const ready = await waitForNextIteration({ expected,
    readControl: () => time === start ? control : { ...control, nextRunAt: new Date(changedDue).toISOString() },
    now: () => time, sleep: async ms => { time += ms; }, report: () => {} });
  assert.equal(ready, true);
  assert.equal(time, changedDue);
});

test('honors a deadline that arrives before the next iteration', async () => {
  let time = start;
  const deadline = start + 20_000;
  const ready = await waitForNextIteration({ expected,
    readControl: () => ({ ...control, deadline: new Date(deadline).toISOString() }),
    now: () => time, sleep: async ms => { time += ms; }, report: () => {} });
  assert.equal(ready, false);
  assert.equal(time, deadline);
});

test('retries transient API failures, with a bound on consecutive failures', async () => {
  let reads = 0;
  let time = due;
  const options = { expected, now: () => time,
    sleep: async ms => { time += ms; }, report: () => {} };
  assert.equal(await waitForNextIteration({ ...options,
    readControl: () => { if (++reads === 1) throw new Error('temporary'); return control; } }), true);
  assert.equal(reads, 2);
  reads = 0;
  await assert.rejects(waitForNextIteration({ ...options,
    readControl: () => { reads++; throw new Error('unavailable'); } }), /five attempts/);
  assert.equal(reads, 5);
});
