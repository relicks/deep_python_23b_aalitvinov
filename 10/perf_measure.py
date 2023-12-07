import json
import statistics as st
import timeit

import cjson
import ujson


def bench(func, n_runs=5, n_loops=10):
    race = timeit.repeat(func, repeat=n_runs, number=n_loops)
    race = [run / n_loops for run in race]
    mag_order = 3
    infimum = round(min(race) * 10**mag_order)
    mean = round(st.mean(race) * 10**mag_order)
    std = round(st.stdev(race) * 10**mag_order, 1)
    print(
        f"\033[1m{mean} ms ± {std} ms\033[0m per loop"
        + f" (mean ± std. dev. of {n_runs} runs, {n_loops} loops each)"
        + f"\nbest time \033[1m\033[32m{infimum}\033[39m ms\033[0m"
    )
    return {"mean": mean, "stdev": std, "min": infimum}


def testing_loads(json_str: str):
    print("Testing 'loads' method...\n")
    print("\nTesting stdlib json 'loads' performance:")
    print("================================")
    json_results = bench(lambda: json.loads(json_str))

    print("\nTesting ujson 'loads' performance:")
    print("==========================")
    ujson_results = bench(lambda: ujson.loads(json_str))
    print(f"{ujson_results['mean'] / json_results['mean']:.2f} of stdlib json time")

    print("\nTesting my very own cjson parser 'loads' performance 😢:")
    print("=========================================")
    cjson_results = bench(lambda: cjson.loads(json_str))
    print(f"{cjson_results['mean'] / json_results['mean']:.2f} of stdlib json time")
    print(f"{cjson_results['mean'] / ujson_results['mean']:.2f} of ujson time")


def testing_dumps(pydict: dict):
    print("Testing 'dumps' method...\n")
    print("\nTesting stdlib json 'dumps' performance:")
    print("================================")
    json_results = bench(lambda: json.dumps(pydict))

    print("\nTesting ujson 'dumps' performance:")
    print("==========================")
    ujson_results = bench(lambda: ujson.dumps(pydict))
    print(f"{ujson_results['mean'] / json_results['mean']:.2f} of stdlib json time")

    print("\nTesting my very own cjson parser 'dumps' performance 😢:")
    print("=========================================")
    cjson_results = bench(lambda: cjson.dumps(pydict))
    print(f"{cjson_results['mean'] / json_results['mean']:.2f} of stdlib json time")
    print(f"{cjson_results['mean'] / ujson_results['mean']:.2f} of ujson time")


def main():
    with open("./data/generated.json") as fd:
        json_str = fd.read()

    testing_loads(json_str)
    print("\n >>------------------------------------------------<<\n")
    testing_dumps(json.loads(json_str))


if __name__ == "__main__":
    main()
