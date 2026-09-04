"""Тудушка: подсчёт задач, фильтры, инлайн-правка и приоритеты."""

import pytest
from conftest import build_control, event

from app.pages import todo
from app.pages.todo import PRIORITIES, TodoBoard, pluralize_tasks


@pytest.mark.parametrize(
    ("count", "word"),
    [
        (0, "задач"),
        (1, "задача"),
        (2, "задачи"),
        (4, "задачи"),
        (5, "задач"),
        (11, "задач"),
        (12, "задач"),
        (14, "задач"),
        (21, "задача"),
        (22, "задачи"),
        (25, "задач"),
        (111, "задач"),
    ],
)
def test_pluralize_tasks(count, word):
    assert pluralize_tasks(count) == word


@pytest.fixture
def board(page):
    return build_control(TodoBoard())


def add_task(board, name):
    board.new_task.value = name
    import asyncio

    asyncio.run(board.add_clicked(event(board.new_task, "submit")))
    return board.tasks.controls[-1]


def test_add_clears_input_and_appends_task(board):
    task = add_task(board, "Написать тесты")
    assert board.new_task.value == ""
    assert len(board.tasks.controls) == 1
    assert task.task_name == "Написать тесты"


def test_empty_input_adds_nothing(board):
    board.new_task.value = ""
    import asyncio

    asyncio.run(board.add_clicked(event(board.new_task, "submit")))
    assert board.tasks.controls == []


def test_seed_adds_demo_tasks(board):
    board.seed_clicked(event(board))
    assert len(board.tasks.controls) == 3
    assert {t.priority for t in board.tasks.controls} == {"high", "normal", "low"}


def test_progress_and_counter_follow_completion(board):
    board.seed_clicked(event(board))
    first = build_control(board.tasks.controls[0])
    first.display_task.value = True
    first.status_changed(event(first.display_task, "change"))

    board.before_update()
    assert first.completed is True
    assert board.items_left.value == "Осталось 2 задачи"
    assert board.progress.value == pytest.approx(1 / 3)
    assert "выполнено 1 из 3" in board.progress_label.value


def test_filter_hides_tasks_of_other_kinds(board):
    board.seed_clicked(event(board))
    done = build_control(board.tasks.controls[0])
    done.display_task.value = True
    done.status_changed(event(done.display_task, "change"))

    board.filter_tabs.selected_index = todo.FILTER_ACTIVE
    board.before_update()
    assert [t.visible for t in board.tasks.controls] == [False, True, True]

    board.filter_tabs.selected_index = todo.FILTER_COMPLETED
    board.before_update()
    assert [t.visible for t in board.tasks.controls] == [True, False, False]

    board.filter_tabs.selected_index = todo.FILTER_ALL
    board.before_update()
    assert all(t.visible for t in board.tasks.controls)


def test_clear_completed_removes_only_done(board):
    board.seed_clicked(event(board))
    done = build_control(board.tasks.controls[1])
    done.display_task.value = True
    done.status_changed(event(done.display_task, "change"))

    board.clear_clicked(event(board))
    assert len(board.tasks.controls) == 2
    assert done not in board.tasks.controls


def test_delete_removes_task(board):
    task = build_control(add_task(board, "Удалить меня"))
    task.delete_clicked(event(task))
    assert board.tasks.controls == []


def test_inline_edit_switches_views_and_saves(board):
    task = build_control(add_task(board, "Старое имя"))
    assert task.display_view.visible is True

    task.edit_clicked(event(task))
    assert task.edit_view.visible is True
    assert task.edit_name.value == "Старое имя"

    task.edit_name.value = "Новое имя"
    task.save_clicked(event(task))
    assert task.display_task.label == "Новое имя"
    assert task.display_view.visible is True
    assert task.edit_view.visible is False


def test_priority_setter_updates_badge(board):
    task = build_control(add_task(board, "Приоритет"))
    task._priority_setter("high")(event(task))
    assert task.priority == "high"
    assert task.priority_badge.content.value == PRIORITIES["high"][0]
    assert task.priority_badge.content.color == PRIORITIES["high"][1]


def test_build_returns_page_with_board(page):
    root = todo.build()
    assert root.controls
