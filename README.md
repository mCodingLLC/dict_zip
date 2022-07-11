# Fast zipping for dict subclasses

Like `zip` but for corresponding dictionaries (dicts with the same keys).
`dict_zip` takes any number of dictionaries and gives you an iterable of corresponding elements of those dictionaries.
Iteration order is guaranteed to be the iteration order of the first argument.

Signature:
```
dict_zip(d1, ..., dn) -> iterable of (key, v1, ..., vn)
```

For example:

```python3
from dict_zip import dict_zip


def main():
    prices = {"apple": 1.00, "banana": 2.50, "chocolate": 3.00}
    quantities = {"apple": 12, "banana": 6, "chocolate": 1}
    costs = {"apple": 1, "banana": "two", "chocolate": "three"}

    for name, price, quantity, cost in dict_zip(prices, quantities, costs):
        print(f"Item: {name}, Profit: {(price - cost) * quantity}")

if __name__ == "__main__":
    main()
```

WARNING: `dict_zip` is intended for use with `dict` and `dict` subclasses only, not general mappings.
`dict_zip` is implemented in C and does NOT call any dictionary methods like
`__getitem__`, `keys`, `values`, `items`, `__hash__`, or `__iter__`.
Instead, we leverage the internal structure of a Python `dict` to walk the memory directly.
This can have unexpected consequences such as a `defaultdict` raising an error for a missing
key instead of inserting it.
Basically, all arguments are operated on as if they were `dict`s.

Note: `dict_zip` is strict, meaning the keys of every argument must be equal
(insertion order does not matter) or you will get `ValueError` either on construction
if the lengths differ or a `KeyError` during iteration for a missing key.
Modifying any of the dicts during iteration is not allowed.




There is some parallel between dict zipping and SQL joins (left, inner, outer, etc.), 
but only strict zipping is currently supported.
I'm open to pull requests that implement these other joins,
but have no plans to implement them myself.