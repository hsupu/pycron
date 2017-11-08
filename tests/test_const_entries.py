from pycron.run_id_generator import RunIdGeneratorType


def print_enum():
    items = RunIdGeneratorType.entries()
    print(items)


if __name__ == '__main__':  # pragma: no cover
    print_enum()
