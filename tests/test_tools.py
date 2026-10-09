import pytest
from tools import (
    marks_to_grade_points, calculate_semester_gpa, calculate_new_cgpa,
    required_gpa_for_target, get_semester_courses, get_remaining_credit_hours,
)


@pytest.mark.parametrize("marks,gp", [(100, 4.0), (85, 4.0), (84, 3.7), (78, 3.3),
                                      (70, 3.0), (50, 1.0), (49, 0.0)])
def test_marks_to_grade_points(marks, gp):
    assert marks_to_grade_points(marks) == gp


def test_marks_out_of_range():
    assert str(marks_to_grade_points(150)).startswith("Error")
    assert str(marks_to_grade_points(-1)).startswith("Error")


def test_semester_gpa():
    assert calculate_semester_gpa([3.0, 4.0], [3, 3]) == 3.5


@pytest.mark.parametrize("gps,chs", [([], []), ([3.0], [3, 3]), ([5.0], [3]), ([3.0], [0]), ([3.0], [-3])])
def test_semester_gpa_rejects_bad_input(gps, chs):
    assert str(calculate_semester_gpa(gps, chs)).startswith("Error")


def test_new_cgpa():
    assert calculate_new_cgpa(3.1, 64, 3.6, 18.5) == pytest.approx(3.21, abs=0.01)


def test_new_cgpa_rejects_bad_input():
    assert str(calculate_new_cgpa(5.0, 64, 3.0, 18)).startswith("Error")
    assert str(calculate_new_cgpa(3.0, -1, 3.0, 18)).startswith("Error")
    assert str(calculate_new_cgpa(3.0, 0, 3.0, 0)).startswith("Error")


def test_required_gpa():
    assert required_gpa_for_target(3.4, 3.0, 64, 18.5) == pytest.approx(4.78, abs=0.01)
    assert required_gpa_for_target(3.4, 3.0, 64, 55.5) == pytest.approx(3.86, abs=0.01)


def test_required_gpa_rejects_bad_input():
    assert str(required_gpa_for_target(3.4, 3.0, 64, 0)).startswith("Error")
    assert str(required_gpa_for_target(5.0, 3.0, 64, 18)).startswith("Error")


def test_remaining_credit_hours():
    assert get_remaining_credit_hours(4) == 70.0
    assert get_remaining_credit_hours(5) == 51.5
    assert get_remaining_credit_hours(4, 5) == 18.5
    assert get_remaining_credit_hours(4, 6) == 37.0
    assert get_remaining_credit_hours(4, 7) == 55.5
    assert str(get_remaining_credit_hours(9)).startswith("Error")


def test_semester_courses():
    assert "Artificial Intelligence" in get_semester_courses(5)
    assert str(get_semester_courses(0)).startswith("Error")
