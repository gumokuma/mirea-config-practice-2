# Практическая работа № 2

РТУ МИРЭА · Конфигурационное управление

Медведков Александр Михайлович · ИКБО-24-25 · вариант 15

## 1. Что делает программа

На вход подаю имя пакета Rust и его точную версию. Программа читает
индекс Cargo по HTTP и находит строку нужной версии. Из неё берутся имена
прямых зависимостей и ограничения на их версии. Для чтения индекса
используется стандартная библиотека Python.
## 2. Как запустить

Нужен Python 3.9 или новее. Установка библиотек и сборка не требуются.
Команды выполняются из корня проекта. На Windows используйте `run.bat`
или `python src/main.py`. Для запуска тестов выполните `run.bat test`
или `python -m unittest discover -s tests -v`.

- `--package ИМЯ` — Обязательное имя корневого пакета
- `--version X.Y.Z` — Обязательная точная версия, допустимы суффиксы SemVer
- `--repo URL_ИЛИ_ПУТЬ` — URL sparse-индекса, по умолчанию `https://index.crates.io`. В тестовом режиме — путь к JSON
- `--test` — Включает тестовый репозиторий. В нём версия проверяется синтаксически
- `--max-depth N` — Максимальное расстояние от корня. При 0 граф состоит из корня
- `--exclude ТЕКСТ` — Исключает зависимости, содержащие подстроку. Регистр учитывается
- `--mode graph` — Выводит PlantUML. Режим по умолчанию
- `--mode direct` — Показывает все прямые зависимости из записи указанной версии Cargo
- `--mode order` — Показывает порядок, в котором зависимости предшествуют родителям
- `--ascii` — Добавляет ASCII-дерево после PlantUML в режиме `graph`

Некорректные параметры возвращают код 2. Ошибки чтения индекса или JSON
и отсутствие заданной версии возвращают код 1.

## 3. Обход графа

Для обхода использовал очередь BFS. Сначала программа добавляет корень,
затем его соседей и только потом следующий уровень. Повторно найденная
вершина не попадает в очередь, но ребро сохраняется.

JSON-объект связывает имена из заглавных латинских букв со списками
прямых зависимостей. Каждая зависимость имеет собственную запись. В
примере из `tests/fixtures/graph.json` пакеты B и D образуют цикл,
а D является общей зависимостью для B и C.

```bat
run.bat --test --repo tests/fixtures/graph.json --package A --version 1.0.0 --ascii
run.bat --test --repo tests/fixtures/graph.json --package A --version 1.0.0 --max-depth 1 --ascii
run.bat --test --repo tests/fixtures/graph.json --package A --version 1.0.0 --exclude B --mode order
run.bat --test --repo tests/fixtures/graph.json --package A --version 1.0.0 --mode order
run.bat --test --repo tests/fixtures/graph.json --package F --version 1.0.0 --mode order
```

Первая команда показывает повторные ссылки с меткой `[seen]`.
Вторая оставляет только рёбра A → B и A → C. Третья выдаёт
`D, E, C, A` по одной строке. Четвёртая выдаёт `E` и сообщает
`Cycle blocks: A, B, C, D`. Пятая выдаёт только `F`.

## 4. Примеры диаграмм

```bat
run.bat --package num-integer --version 0.1.46 --mode direct
run.bat --package num-integer --version 0.1.46 --mode order
run.bat --package num-integer --version 0.1.46 > num-integer.puml
run.bat --package unicode-normalization --version 0.1.24 > unicode-normalization.puml
run.bat --package walkdir --version 2.5.0 > walkdir.puml
```

Файлы `.puml` можно открыть в PlantUML. Граф направлен от пакета к
его зависимостям. Транзитивные версии выбираются из доступных на момент
запроса, поэтому номера могут меняться.

При проверке получились такие зависимости.

- `num-integer@0.1.46` — `num-integer → num-traits@0.2.19 → autocfg@1.5.1`
- `unicode-normalization@0.1.24` — `unicode-normalization → tinyvec@1.13.3`
- `walkdir@2.5.0` — `walkdir → same-file@1.0.6`

## 5. Сверка с Cargo

Для проверки создайте отдельный Cargo-проект командой
`cargo new cargo-check`. Добавьте в его секцию `[dependencies]`
одну из строк и запустите `cargo tree -e normal,build --target x86_64-pc-windows-msvc` из каталога
проекта. Перед следующим сравнением замените строку зависимости.

```toml
num-integer = "=0.1.46"
unicode-normalization = "=0.1.24"
walkdir = "=2.5.0"
```

Сравнение выполнено с Cargo 1.99.1 для цели `x86_64-pc-windows-msvc`.

- `num-integer@0.1.46` — Рёбра и версии совпали. Cargo помечает `autocfg` как сборочную зависимость `num-traits`.
- `unicode-normalization@0.1.24` — Рёбра и версии совпали. В обоих графах есть только `tinyvec@1.13.3` под корнем.
- `walkdir@2.5.0` — Cargo добавил `winapi-util@0.1.11` к `walkdir` и `same-file`, далее `windows-sys@0.61.2` и `windows-link@0.2.1`. Эти рёбра относятся к ветке Windows.

В режиме `order` для `num-integer` получен порядок
`autocfg@1.5.1 → num-traits@0.2.19 → num-integer@0.1.46`.
Он соответствует направлению предшествования в дереве Cargo. Во время
проверки Cargo сообщил о скачивании в порядке `autocfg → num-integer →
num-traits`. Скачивание может выполняться параллельно, а наш порядок
гарантирует, что каждая зависимость стоит раньше своего потребителя.

Граф CLI включает обязательные обычные и сборочные зависимости общего
назначения из выбранного реестра. Cargo также учитывает `Cargo.lock`,
целевую платформу, возможности и глобальное согласование версий.
В режиме `direct` видны все прямые записи индекса, включая условные
и опциональные.

[Формат индекса](https://doc.rust-lang.org/cargo/reference/registry-index.html)
· [Требования к версиям](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)
· [cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html)

## Устройство программы

- `main.py` проверяет настройки и выбирает режим вывода.
- `registry.py` строит путь записи, читает и кэширует версии пакета.
- `semver.py` подбирает максимальную доступную версию для каждого ребра.
- `graph.py` строит смежность очередью BFS. Уже добавленные вершины
  повторно не помещаются в очередь, а рёбра цикла сохраняются.
- `output.py` формирует PlantUML и ASCII-дерево и вычисляет порядок
  загрузки алгоритмом Кана. При цикле показывает заблокированные вершины.

В истории Git по одному коммиту на каждый этап. Чтобы посмотреть
прототип с выводом параметров и этап с прямыми зависимостями,
используйте `git log --oneline` и `git show <коммит>:src/main.py`.
