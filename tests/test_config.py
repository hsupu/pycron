from pycron import config


def test_task_schema():
    config_map = config.parse_task_config_str('''
executable: /Users/xp/echo.sh
cron: "0 * * * * * *"
user: xp
group: xp
workDir: /Users/xp
env:
  a: 1
  b: 2
args:
  - a
  - b
  - c
stdin:
  source: NONE
stdout:
  target: NONE
stderr:
  target: NONE

''')
    print(config_map)


def test_parse_config_files():
    config_ret = config.parse_config_files(config_dir='/Users/xp/code/python/pycron/dist')
    print(config_ret)


if __name__ == '__main__':  # pragma: no cover
    test_parse_config_files()
