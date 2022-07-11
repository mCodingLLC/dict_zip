import dataclasses
import timeit
from dict_zip import dict_zip


def dict_zip_py(*dicts):
    if not dicts:
        return

    n = len(dicts[0])
    if any(len(d) != n for d in dicts):
        raise ValueError("arguments must have the same length")

    for key, first_val in dicts[0].items():
        yield key, first_val, *(other[key] for other in dicts[1:])


def dict_zip_py_optimized(*dicts):
    if not dicts:
        return

    n = len(dicts[0])
    if any(len(d) != n for d in dicts):
        raise ValueError("arguments must have the same length")

    dict_count = len(dicts)
    if dict_count == 1:
        yield from d1.items()
    if dict_count == 2:
        d1, d2 = dicts
        for key, first_val in d1.items():
            yield key, first_val, d2[key]
    elif dict_count == 3:
        d1, d2, d3 = dicts
        for key, first_val in d1.items():
            yield key, first_val, d2[key], d3[key]
    else:
        first_dict, *others = dicts
        for key, first_val in first_dict.items():
            yield key, first_val, *[other[key] for other in others]


work = "k = max(v1+v2, 2*v1 - v2)"

control_lbl = "single dict"
stmts = {
    "single dict": f"""
for key, v1 in d1.items():
    v2 = v1
    {work}
""",
    "dict_zip_c": f"""
for key, v1, v2 in dict_zip(d1, d2):
    {work}
""",
    "2 d[key]'s": f"""
if len(d1) != len(d2):
    raise ValueError("length")
for key in d1:
    v1 = d1[key]
    v2 = d2[key]
    {work}
""",
    "items()+d[key]": f"""
if len(d1) != len(d2):
    raise ValueError("length")
for key, v1 in d1.items():
    v2 = d2[key]
    {work}
""",
    "dict_zip_py": f"""
for key, v1, v2 in dict_zip_py(d1, d2):
    {work}
""",
    "dict_zip_py opt": f"""
for key, v1, v2 in dict_zip_py_optimized(d1, d2):
    {work}
""",
}


def perf_dicts(d1, d2):
    n = 1000

    items = []
    just = max(len(lbl) for lbl in stmts.keys())
    for lbl, stmt in stmts.items():
        t = timeit.timeit(
            stmt=stmt,
            globals=globals() | {"d1": dict(d1), "d2": dict(d2)},
            number=n,
        )
        t = t / n * 10e6
        if lbl == control_lbl:
            control_time = t

        s = (
            lbl.rjust(just)
            + f" time: {t:.2f} us, {t/control_time:.2f}x or {t/control_time*100:.0f}% of control time"
        )
        items.append((t, s))

    items.sort()
    for idx, (t, s) in enumerate(items):
        print(f"{idx}. {s}")


@dataclasses.dataclass(frozen=True, slots=True)
class Data:
    x: int
    y: str


def main():
    print("abc")
    perf_dicts(d1={"a": 1, "b": 2, "c": 3}, d2={"a": 4, "b": 5, "c": 6})
    print()

    print("i: i range 100")
    perf_dicts(d1={i: i for i in range(100)}, d2={i: i for i in range(100)})
    print()

    print("str(i): i range 100")
    perf_dicts(
        d1={f"{i}xxxxxx": i for i in range(100)},
        d2={f"{i}xxxxxx": i for i in range(100)},
    )
    print()

    print("str(i): i range 1000")
    perf_dicts(
        d1={f"{i}xxxxxx": i for i in range(1000)},
        d2={f"{i}xxxxxx": i for i in range(1000)},
    )
    print()

    print("Data(i, str(i)): i range 100")
    perf_dicts(
        d1={Data(i, f"{i}"): i for i in range(100)},
        d2={Data(i, f"{i}"): i for i in range(100)},
    )
    print()


if __name__ == "__main__":
    main()
