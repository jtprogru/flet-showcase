# Makefile для локальной разработки todo (Flet + uv)

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

UV ?= uv
RUN := $(UV) run
PYTHON_VERSION ?= 3.14
SRC ?= main.py

.PHONY: help
help: ## Показать список доступных целей
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

## --- Окружение ---------------------------------------------------------

.PHONY: venv
venv: ## Создать .venv с нужной версией Python
	$(UV) venv --python $(PYTHON_VERSION)

.PHONY: install
install: ## Установить зависимости, включая dev-группу
	$(UV) sync --all-groups

.PHONY: install-prod
install-prod: ## Установить только runtime-зависимости
	$(UV) sync --no-dev

.PHONY: lock
lock: ## Пересобрать uv.lock
	$(UV) lock

.PHONY: upgrade
upgrade: ## Обновить все зависимости до последних допустимых версий
	$(UV) lock --upgrade
	$(UV) sync --all-groups

.PHONY: outdated
outdated: ## Показать устаревшие зависимости
	$(UV) tree --outdated --depth 1

## --- Запуск ------------------------------------------------------------

.PHONY: run
run: ## Запустить витрину нативным окном (GUI)
	$(RUN) flet run $(SRC)

.PHONY: run-web
run-web: ## Запустить витрину в браузере
	$(RUN) flet run --web $(SRC)

.PHONY: watch
watch: ## Запустить GUI с перезапуском при изменении файлов
	$(RUN) flet run --recursive $(SRC)

.PHONY: shell
shell: ## Python REPL в окружении проекта
	$(RUN) python

## --- Качество кода -----------------------------------------------------

.PHONY: fmt
fmt: ## Отформатировать код (ruff format + fix)
	$(RUN) --group lint ruff format .
	$(RUN) --group lint ruff check --fix .

.PHONY: smoke
smoke: ## Собрать все страницы без запуска GUI (быстрая проверка)
	$(RUN) python -c "from app.theme import ThemeController; \
	from app.shell import Shell, SECTIONS, build_appbar; \
	c = ThemeController(); s = Shell(c); s.build(); build_appbar(c, s); \
	[SECTIONS[i][3](c) for i in range(len(SECTIONS))]; \
	print(f'OK: {len(SECTIONS)} разделов собираются')"

.PHONY: lint
lint: ## Проверить код без изменений
	$(RUN) --group lint ruff format --check .
	$(RUN) --group lint ruff check .

.PHONY: typecheck
typecheck: ## Проверить типы (mypy)
	$(RUN) --group lint mypy $(SRC) app tests

.PHONY: test
test: ## Прогнать тесты
	$(RUN) --group test pytest

.PHONY: test-cov
test-cov: ## Тесты с покрытием (порог 80%)
	$(RUN) --group test pytest --cov --cov-report=term-missing

.PHONY: test-html
test-html: ## Отчёт о покрытии в htmlcov/index.html (откроется в браузере)
	$(RUN) --group test pytest --cov --cov-report=html
	@if command -v open >/dev/null; then open htmlcov/index.html; \
	elif command -v xdg-open >/dev/null; then xdg-open htmlcov/index.html; \
	else echo "Отчёт: htmlcov/index.html"; fi

.PHONY: check
check: lint test smoke ## Полная проверка перед коммитом

## --- Сборка ------------------------------------------------------------

# Первая сборка скачивает Flutter SDK (несколько ГБ) — это нормально и делается один раз.
.PHONY: build-macos
build-macos: ## Собрать .app для macOS
	$(RUN) flet build macos --yes

.PHONY: build-linux
build-linux: ## Собрать приложение для Linux
	$(RUN) flet build linux --yes

.PHONY: build-windows
build-windows: ## Собрать приложение для Windows
	$(RUN) flet build windows --yes

.PHONY: build-web
build-web: ## Собрать статическую web-версию
	$(RUN) flet build web --yes

# flet требует целевую платформу даже для матрицы (берём web — собирается везде)
# и после вывода таблицы всегда выходит с кодом 1, поэтому его не считаем ошибкой.
.PHONY: build-matrix
build-matrix: ## Показать, что и на чём можно собрать
	$(RUN) flet build web --show-platform-matrix --skip-flutter-doctor || [ $$? -eq 1 ]

## --- Обслуживание ------------------------------------------------------

.PHONY: clean
clean: ## Удалить артефакты сборки и кеши
	rm -rf build dist .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: distclean
distclean: clean ## Удалить ещё и виртуальное окружение
	rm -rf .venv
