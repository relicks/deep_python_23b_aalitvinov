import argparse
from random import sample

import ujson
from faker import Faker


def json_gen(dict_len: int) -> None:
    fake = Faker()

    dict_keys = (fake.pystr(min_chars=15, max_chars=100) for _ in range(dict_len))
    value_pool = (
        [fake.paragraph(nb_sentences=5) for _ in range(dict_len)]
        + fake.words(dict_len)
        + [
            fake.pylist(nb_elements=100, value_types=[str, int, float, bool])
            for _ in range(dict_len // 100)
        ]
        + [fake.pyint() for _ in range(dict_len)]
        + [None] * (dict_len // 1000)
    )
    json_dict = dict(zip(dict_keys, sample(value_pool, dict_len), strict=True))

    print("Saving to file")
    with open("./data/generated.json", "w") as fd:
        ujson.dump(json_dict, fd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--json-length", type=int, default=200_000)
    args = parser.parse_args()
    print(f"Generating JSON with {args.json_length} keys")
    json_gen(args.json_length)


if __name__ == "__main__":
    main()
