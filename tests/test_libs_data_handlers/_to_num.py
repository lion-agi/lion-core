import pytest

from lion_core.libs.data_handlers._to_num import to_num


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("42", 42),
        ("-42", -42),
        ("+42", 42),
        ("0", 0),
    ],
)
def test_to_num_integer(input_str, expected):
    assert to_num(input_str, num_type=int) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("3.14", 3.14),
        ("-3.14", -3.14),
        ("+3.14", 3.14),
        ("0.0", 0.0),
        (".5", 0.5),
        ("5.", 5.0),
    ],
)
def test_to_num_float(input_str, expected):
    assert to_num(input_str, num_type=float) == pytest.approx(expected)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("2/3", 2 / 3),
        ("-2/3", -2 / 3),
        ("1/2", 0.5),
        ("4/2", 2.0),
    ],
)
def test_to_num_fraction(input_str, expected):
    assert to_num(input_str, num_type=float) == pytest.approx(expected)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("1e3", 1000.0),
        ("1E-3", 0.001),
        ("-1.23e4", -12300.0),
        ("1.23E+4", 12300.0),
    ],
)
def test_to_num_scientific_notation(input_str, expected):
    assert to_num(input_str, num_type=float) == pytest.approx(expected)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("1+2j", 1 + 2j),
        ("-1-2j", -1 - 2j),
        ("3j", 3j),
        ("-3j", -3j),
    ],
)
def test_to_num_complex(input_str, expected):
    assert to_num(input_str, num_type=complex) == expected


@pytest.mark.parametrize(
    "input_str, precision, expected",
    [
        ("3.14159", 2, 3.14),
        ("3.14159", 4, 3.1416),
        ("1.23456789", 3, 1.235),
    ],
)
def test_to_num_precision(input_str, precision, expected):
    assert to_num(input_str, num_type=float, precision=precision) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    "input_str, upper_bound",
    [
        ("100", 50),
        ("1000", 999),
        ("3.14", 3),
    ],
)
def test_to_num_upper_bound(input_str, upper_bound):
    with pytest.raises(ValueError):
        to_num(input_str, num_type=float, upper_bound=upper_bound)


@pytest.mark.parametrize(
    "input_str, lower_bound",
    [
        ("10", 20),
        ("-5", 0),
        ("2.5", 3),
    ],
)
def test_to_num_lower_bound(input_str, lower_bound):
    with pytest.raises(ValueError):
        to_num(input_str, num_type=float, lower_bound=lower_bound)


@pytest.mark.parametrize(
    "input_str, num_count, expected",
    [
        ("1 and 2 and 3", 3, [1.0, 2.0, 3.0]),
        ("1, 2, 3, 4", 4, [1.0, 2.0, 3.0, 4.0]),
        ("1.5 2.5 3.5", 3, [1.5, 2.5, 3.5]),
    ],
)
def test_to_num_multiple_numbers(input_str, num_count, expected):
    assert to_num(input_str, num_count=num_count) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "not a number",
        "one two three",
        "a1b2c3",
    ],
)
def test_to_num_invalid_input(input_str):
    with pytest.raises(ValueError):
        to_num(input_str)


@pytest.mark.parametrize(
    "num_type",
    [
        "invalid",
        str,
        list,
    ],
)
def test_to_num_invalid_num_type(num_type):
    with pytest.raises(ValueError):
        to_num("42", num_type=num_type)


@pytest.mark.parametrize(
    "input_str",
    [
        "0x1A",
        "0b1010",
    ],
)
def test_to_num_unsupported_formats(input_str):
    with pytest.raises(ValueError):
        to_num(input_str)


def test_to_num_empty_string():
    with pytest.raises(ValueError):
        to_num("")


def test_to_num_whitespace():
    with pytest.raises(ValueError):
        to_num("   ")


def test_to_num_mixed_types():
    assert to_num("1 and 2.5 and 3+2j", num_count=3) == [1.0, 2.5, 3 + 2j]


def test_to_num_with_text():
    assert to_num("The answer is 42", num_count=1) == [42.0]


def test_to_num_large_number():
    assert to_num("1234567890123456789", num_type=int) == 1234567890123456789


def test_to_num_very_small_float():
    assert to_num("1e-100", num_type=float) == 1e-100


@pytest.mark.parametrize(
    "input_str, num_type, expected",
    [
        ("inf", float, float("inf")),
        ("-inf", float, float("-inf")),
        ("nan", float, float("nan")),
    ],
)
def test_to_num_special_floats(input_str, num_type, expected):
    result = to_num(input_str, num_type=num_type)
    if input_str == "nan":
        assert result != result  # NaN is not equal to itself
    else:
        assert result == expected


def test_to_num_no_numbers():
    with pytest.raises(ValueError):
        to_num("No numbers here", num_count=1)


def test_to_num_fewer_numbers_than_requested():
    with pytest.raises(ValueError):
        to_num("1 2 3", num_count=4)


def test_to_num_more_numbers_than_requested():
    assert to_num("1 2 3 4 5", num_count=3) == [1.0, 2.0, 3.0]


def test_to_num_with_thousands_separator():
    assert to_num("1,000,000", num_type=int) == 1000000


def test_to_num_different_fraction_formats():
    assert to_num("1/2 0.5 50%", num_count=3) == [0.5, 0.5, 0.5]


def test_to_num_mixed_case_scientific_notation():
    assert to_num("1e3 1E3 1e+3 1E-3", num_count=4) == [1000.0, 1000.0, 1000.0, 0.001]


def test_to_num_complex_with_spaces():
    assert to_num("1 + 2j", num_type=complex) == 1 + 2j


def test_to_num_int_with_plus_sign():
    assert to_num("+42", num_type=int) == 42


def test_to_num_float_with_plus_sign():
    assert to_num("+3.14", num_type=float) == 3.14


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("1/3", 1 / 3),
        ("2/3", 2 / 3),
        ("10/3", 10 / 3),
    ],
)
def test_to_num_fraction_precision(input_str, expected):
    assert to_num(input_str, num_type=float) == pytest.approx(expected)


def test_to_num_non_string_input():
    assert to_num(42) == 42.0
    assert to_num(3.14) == 3.14
    assert to_num(1 + 2j) == 1 + 2j


def test_to_num_list_input():
    with pytest.raises(TypeError):
        to_num([1, 2, 3])


def test_to_num_dict_input():
    with pytest.raises(TypeError):
        to_num({"a": 1, "b": 2})


def test_to_num_bool_input():
    assert to_num(True) == 1.0
    assert to_num(False) == 0.0


@pytest.mark.parametrize(
    "input_str, num_type, expected",
    [
        ("42", "int", 42),
        ("3.14", "float", 3.14),
        ("1+2j", "complex", 1 + 2j),
    ],
)
def test_to_num_string_num_type(input_str, num_type, expected):
    assert to_num(input_str, num_type=num_type) == expected


def test_to_num_performance_large_input(benchmark):
    large_input = " ".join([str(i) for i in range(10000)])
    result = benchmark(to_num, large_input, num_count=10000)
    assert len(result) == 10000
    assert result[0] == 0.0
    assert result[-1] == 9999.0


# File: tests/test_to_num.py
