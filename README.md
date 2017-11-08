# pycron

A scheduler using cron syntax written in python.

## Dependencies

```bash
pip install -r requirements.txt
```

## Usage

run pycron

```bash

```

report format

```json
{
  
}
```

## Config

main config

```yaml

```

task config

```yaml

```

## Architecture

- Task: a execution blueprint (config) for scheduler.
- Watcher: wait work until it's done, then report status.
- Worker: do "exec" syscall, write stdin and read stdout/stderr.

---

- RunIdGenerator: generate run_id, of carouse.
- Reporter: report work-event to another service.
- StdinSource: support a fd which is piped to stdin.
- StdoutTarget: support a fd which stdout/stderr is piped to.

## TODO

## License

The BSD 3-Clause License

