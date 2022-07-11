#    Copyright 2022 MCODING, LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#    dict_zip module written and maintained
#    by James Murphy <james@mcoding.io>


import dict_zip
import collections
import pytest


def test_dict_zip_module_has_version():
    actual = dict_zip.__version__
    assert type(actual) is tuple
    assert len(actual) == 3
    major, minor, patch = actual
    assert (type(major), type(minor), type(patch)) == (int, int, int)
    assert major >= 0
    assert minor >= 0
    assert patch >= 0


def test_dict_zip_callable_is_in_dict_zip_module():
    actual = dict_zip.dict_zip
    assert callable(actual)


def test_zip_no_dicts_is_empty():
    expected = []
    actual = list(dict_zip.dict_zip())
    assert actual == expected


def test_zip_one_dict_is_dict_items():
    d1 = {"a": 1, "b": 2, "c": 3}
    expected = [("a", 1), ("b", 2), ("c", 3)]
    actual = list(dict_zip.dict_zip(d1))
    assert actual == expected


def test_zip_two_dicts():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 4, "b": 5, "c": 6}
    expected = [("a", 1, 4), ("b", 2, 5), ("c", 3, 6)]
    actual = list(dict_zip.dict_zip(d1, d2))
    assert actual == expected


def test_zip_dict_uses_order_of_left_dict():
    d1 = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
    d2 = {"b": 0, "c": 0, "a": 0, "e": 0, "d": 0}
    expected = [("a", 1, 0), ("b", 2, 0), ("c", 3, 0), ("d", 4, 0), ("e", 5, 0)]
    actual = list(dict_zip.dict_zip(d1, d2))
    assert actual == expected

    expected = [("b", 0, 2), ("c", 0, 3), ("a", 0, 1), ("e", 0, 5), ("d", 0, 4)]
    actual = list(dict_zip.dict_zip(d2, d1))
    assert actual == expected


def test_zip_many_dicts():
    n = 100
    dicts = ({"a": 0, "b": 1, "c": 2} for _ in range(n))
    it = dict_zip.dict_zip(*dicts)
    expected = [
        ("a",) + (0,) * n,
        ("b",) + (1,) * n,
        ("c",) + (2,) * n,
    ]
    actual = list(it)
    assert actual == expected


def test_zip_dicts_about_to_dealloc():
    it = dict_zip.dict_zip({"a": 0, "b": 1, "c": 2}, {"a": 0, "b": 1, "c": 2})
    expected = [("a", 0, 0), ("b", 1, 1), ("c", 2, 2)]
    actual = list(it)
    assert actual == expected


def test_zip_ordered_dicts():
    d1 = collections.OrderedDict({"a": 1, "b": 2, "c": 3})
    d2 = collections.OrderedDict({"a": 4, "b": 5, "c": 6})
    expected = [("a", 1, 4), ("b", 2, 5), ("c", 3, 6)]
    actual = list(dict_zip.dict_zip(d1, d2))
    assert actual == expected


def test_non_dict_raises():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = []

    with pytest.raises(TypeError):
        actual = dict_zip.dict_zip(d1, d2)


def test_length_based_strictness():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3, "d": 4}

    with pytest.raises(ValueError):
        actual = dict_zip.dict_zip(d1, d2)


def test_key_strictness_second_dict():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "X": 2, "c": 3}

    with pytest.raises(KeyError):
        actual = list(dict_zip.dict_zip(d1, d2))


def test_key_strictness_first_dict():
    d1 = {"a": 1, "X": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    with pytest.raises(KeyError):
        actual = list(dict_zip.dict_zip(d1, d2))


def test_comparison_can_raise():
    class A(str):
        def __eq__(self, o: object) -> bool:
            if type(o) is not A:
                raise NotImplementedError

            return super().__eq__(o)

        def __hash__(self) -> int:
            return super().__hash__()

    d1 = {"a": 1, A("b"): 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    with pytest.raises(NotImplementedError):
        actual = list(dict_zip.dict_zip(d1, d2))


def test_changed_dict_size_raises():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    it = dict_zip.dict_zip(d1, d2)

    d1["d"] = 4

    with pytest.raises(RuntimeError):
        actual = next(it)


def test_other_dict_changed_dict_size_raises():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    it = dict_zip.dict_zip(d1, d2)

    d2["d"] = 4

    with pytest.raises(RuntimeError):
        actual = next(it)


def test_changed_dict_size_mid_iteration_raises():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    it = dict_zip.dict_zip(d1, d2)
    next(it)

    d1["d"] = 4

    with pytest.raises(RuntimeError):
        actual = next(it)


def test_other_dict_changed_dict_size_mid_iteration_raises():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = {"a": 1, "b": 2, "c": 3}

    it = dict_zip.dict_zip(d1, d2)
    next(it)

    d2["d"] = 4

    with pytest.raises(RuntimeError):
        actual = next(it)


def test_defaultdict_okay_if_strict():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = collections.defaultdict(int, {"a": 4, "b": 5, "c": 6})
    expected = [("a", 1, 4), ("b", 2, 5), ("c", 3, 6)]
    actual = list(dict_zip.dict_zip(d1, d2))
    assert actual == expected


def test_defaultdict_raises_if_key_added():
    d1 = {"a": 1, "b": 2, "c": 3}
    d2 = collections.defaultdict(int, {"a": 4, "b": 5, "d": 6})

    with pytest.raises(KeyError):
        actual = list(dict_zip.dict_zip(d1, d2))
