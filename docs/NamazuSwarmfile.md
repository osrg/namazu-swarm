# NamazuSwarmfile specification V0

Namazu Swarm requires a special script named `NamazuSwarmfile` with in the root directory of the container.

```dockerfile
FROM alpine
...
ADD NamazuSwarmfile /
RUN chmod +x /NamazuSwarmfile

CMD "hack for keep the container running" && tail -f /dev/null
```

`NamazuSwarmfile` must support the argument convention described in this section.

## `/NamazuSwarmfile info-jsonl`
Returns a manifest info immediately.

**Stdout:** [JSON Lines](http://jsonlines.org/).

Example:
```json
{"API":"v0","RequiresPrivileged":true}
```

- `API`: required and needs to be "v0"
- `NotReady`(optional): `true` if the container is not ready for `exec`. Namazu Swarm will wait for ready.
- `RequiresPrivileged`(optional): `true` if the container requires `docker run --privileged`.

**Stderr**: Arbitrary bytes.

## `/NamazuSwarmfile enum-jsonl`
Returns a multiple test commands that will be executed (via `/NamazuSwarmfile exec`) in parallel across the distributed container cluster.
This command does not need to exit immediately.

**Stdout:** [JSON Lines](http://jsonlines.org/).

Example:
```json
{"Command":"go test ./foo"}
{"Command":"go test ./bar"}
{"Command":"go test ./baz"}
```

- `Command`: command string

(TODO) support cost estimation, flakiness estimation, importance (e.g. related to recent git commits), ..

**Stderr**: Arbitrary bytes.

## `/NamazuSwarmfile exec COMMAND`
Executes the command line, which would be included in the list retuned by `/NamazuSwarmfile enum-jsonl`.
`/NamazuSwarmfile exec` can be called multiple times if `unreusable` is `false`.

**Stdout**: Arbitrary bytes.

**Stderr**: Arbitrary bytes.
