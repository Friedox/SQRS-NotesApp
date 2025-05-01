## Шаги для настройки Git Hooks

1. **Найдите директорию `.git/hooks`**
   Каждый Git-проект содержит директорию `.git/hooks`. В этой директории уже есть примеры файлов хуков с расширением `.sample`.

2. **Замените скрипт**
   Найдите скрипт в `.git/hooks` с таким же названием как и в текущем каталоге. Замените содержимое файла хука на ваш собственный скрипт и уберите расширение `.sample`. Убедитесь, что скрипт является исполняемым.

3. **Соблюдайте правильное именование**
   Файл хука должен называться точно так же, как соответствующий файл `.sample`, но без расширения `.sample`.
   Например:
    - Переименуйте `commit-msg.sample` в `commit-msg`.

4. **Протестируйте хук**
   После настройки хука протестируйте его, выполнив соответствующее действие в Git (например, создание коммита, отправку кода и т.д.).

## Пример

Чтобы настроить хук `commit-msg`:
1. Перейдите в директорию `.git/hooks` вашего проекта.
2. Переименуйте `commit-msg.sample` в `commit-msg`.
3. Замените содержимое файла `commit-msg` на ваш скрипт.
4. Сделайте скрипт исполняемым (если необходимо):

```bash
chmod +x .git/hooks/commit-msg
```

## Pre-commit hooks

The project uses pre-commit hooks to ensure code quality and consistency.

### Setup

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Install the git hooks:
```bash
pre-commit install
```

### Available hooks

- **pre-commit-hooks**: Basic file checks (trailing whitespace, file endings, YAML validation)
- **black**: Code formatting
- **ruff**: Fast Python linter

### Usage

Pre-commit hooks run automatically on every commit. To run manually:

```bash
pre-commit run --all-files
```

If a hook fails, fix the issues and try committing again.
