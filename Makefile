# Makefile для локальной разработки todo (Flet + uv)

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

UV ?= uv
RUN := $(UV) run
PYTHON_VERSION ?= 3.12
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
	$(UV) tool run ruff format .
	$(UV) tool run ruff check --fix .

.PHONY: smoke
smoke: ## Собрать все страницы без запуска GUI (быстрая проверка)
	$(RUN) python -c "from app.theme import ThemeController; \
	from app.shell import Shell, SECTIONS, build_appbar; \
	c = ThemeController(); s = Shell(c); s.build(); build_appbar(c, s); \
	[SECTIONS[i][3](c) for i in range(len(SECTIONS))]; \
	print(f'OK: {len(SECTIONS)} разделов собираются')"

.PHONY: lint
lint: ## Проверить код без изменений
	$(UV) tool run ruff format --check .
	$(UV) tool run ruff check .

.PHONY: typecheck
typecheck: ## Проверить типы (mypy)
	$(RUN) --with mypy mypy $(SRC)

.PHONY: test
test: ## Прогнать тесты
	$(RUN) --with pytest pytest -q

.PHONY: test-cov
test-cov: ## Тесты с покрытием
	$(RUN) --with pytest --with pytest-cov pytest --cov=. --cov-report=term-missing

.PHONY: check
check: lint smoke ## Полная проверка перед коммитом

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

.PHONY: build-matrix
build-matrix: ## Показать, что и на чём можно собрать
	$(RUN) flet build --show-platform-matrix

## --- Обслуживание ------------------------------------------------------

.PHONY: clean
clean: ## Удалить артефакты сборки и кеши
	rm -rf build dist .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: distclean
distclean: clean ## Удалить ещё и виртуальное окружение
	rm -rf .venv
