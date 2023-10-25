"""Содержит тесты решения первого пункта домашнего задания #04."""
# pylint: disable=redefined-outer-name
import pytest

from custom_meta import CustomMeta, is_dunder_name, prefix_dict

CLASS_VAR = 50
INST_VAR = "999"


@pytest.fixture()
def custom_class() -> type:
    class CustomClass(metaclass=CustomMeta):
        x = CLASS_VAR

        def __init__(self, val=INST_VAR):
            self.val = val

        def line(self):
            return "from line"

        def __str__(self):
            return "Custom_by_metaclass"

    return CustomClass


def test_class_attrs_get_raises(custom_class: type):
    with pytest.raises(AttributeError):
        _ = custom_class.x  # type: ignore


def test_class_attrs_get(custom_class: type):
    assert custom_class.custom_x == CLASS_VAR  # type: ignore


def test_class_attrs_set_raises(custom_class: type):
    custom_class.some = True  # type: ignore
    with pytest.raises(AttributeError):
        _ = custom_class.some  # type: ignore


def test_class_attrs_set(custom_class: type):
    return_val = (55, "sss")
    custom_class.some = return_val  # type: ignore
    assert custom_class.custom_some == return_val  # type: ignore


def test_inst_attrs_get_raises(custom_class: type):
    inst = custom_class()
    mangled_attrs = ("x", "val", "line", "yyy")
    for attr in mangled_attrs:
        with pytest.raises(AttributeError):
            getattr(inst, attr)


def test_inst_attrs_get(custom_class: type):
    inst = custom_class()
    assert inst.custom_x == CLASS_VAR
    assert inst.custom_val == INST_VAR
    assert inst.custom_line() == "from line"
    assert str(inst) == "Custom_by_metaclass"


def test_inst_attrs_set_raises(custom_class: type):
    inst = custom_class()
    inst.dynamic = "added later"
    with pytest.raises(AttributeError):
        _ = inst.dynamic


def test_inst_attrs_set(custom_class: type):
    inst = custom_class()
    inst.dynamic = "added later"
    assert inst.custom_dynamic == "added later"


@pytest.mark.parametrize(
    "name",
    [
        ("nme", False),
        ("not_a_dunder_name", False),
        ("____", False),
        ("__name", False),
        ("what__", False),
        ("__ява__", False),
        ("__ggg__", True),
        ("__?__", True),
    ],
)
def test_is_dunder_name(name: tuple[str, bool]):
    assert is_dunder_name(name[0]) == name[1]


def test_prefix_dict():
    prefix = "c_pr_"
    sample_dict = {
        "regular_name": object,
        "__stupid_name": ...,
        "ridiculous__": 4 + 2j,
        f"{prefix}art": 9,
        "__special__": False,
    }
    expected_dict = {
        f"{prefix}regular_name": object,
        f"{prefix}art": 9,
        f"{prefix}__stupid_name": ...,
        f"{prefix}ridiculous__": 4 + 2j,
        "__special__": False,
    }

    assert prefix_dict(sample_dict, prefix) == expected_dict
