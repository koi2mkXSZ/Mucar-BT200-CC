# DollarFix: локальный реверс APK через REA + Codex

Исследование ведётся в репозитории Mucar-BT200-CC, но проприетарные файлы никогда не публикуются.

## Запуск (Windows PowerShell 5.1)

В рабочей копии проекта после перехода на ветку research/dollarfix-rea-codex:

    .\scripts\Start-DollarFix-REA.ps1 -ApkPath "C:\Path\To\DollarFix.apk" -QiruiZipPath "C:\Path\To\DollarFix_QIRUI_FULL.zip"

QIRUI ZIP необязателен. Флаг -SkipCodex пропускает Codex. Если локальные сценарии заблокированы, без изменения системной политики:

Если `adb.exe` не найден, скрипт можно запустить с флагом `-InstallAdb`. Тогда он загрузит официальный Android Platform-Tools ZIP с Google в `C:\REA\Project\DollarFix\tools\android\`, не меняя системный PATH и не требуя прав администратора. При наличии существующего ADB можно указать `-AdbPath`.

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-DollarFix-REA.ps1 -ApkPath "C:\Path\To\DollarFix.apk"

## Что выполняется

- Оригинальный APK копируется без изменений, сверяется его SHA-256.
- Формируется JSON inventory: DEX, ELF/ABI, хэши, метаданные подписи, точные вхождения характерных Bluetooth/DPU токенов.
- Вызываются локальные JADX и Apktool, если доступны.
- Фиксируется доступность REA (doctor/providers), а не предполагается по конфигу.
- Codex получает reverse/docs/CODEX_RE_TASK.md; может вызывать REA MCP при подключении.
- Никакого запуска APK, соединения с автомобилем или записи в ECU не выполняется.

## Результаты и приватность

    reverse/input/       original APK / QIRUI (gitignored)
    reverse/work/jadx/   decompiled Java sources (gitignored)
    reverse/work/apktool/ resources and smali (gitignored)
    reverse/work/native/ ELF libraries (gitignored)
    reverse/reports/     inventories, logs and Codex output (gitignored)
    reverse/docs/        authored redacted findings (tracked)

## Ограничения

- Статическая инвентаризация не равна реверсу всего кода, а наличие MCP регистрации не доказывает выполнение REA.
- Модифицированный APK считается готовым только после реализации конкретного патча, успешной сборки, проверки подписи и теста поведения.
- Подпись другим ключом не позволяет обычное обновление установленного DollarFix; не удалять исходное приложение и данные без отдельного безопасного плана.
- Не отключать лицензионные, авторизационные и защитные проверки. Цель — только чтение/отображение уже существующего пробега.

## Тест инструмента инвентаризации

    python -m unittest discover -s reverse/tests -v

Тесты на синтетическом APK, без внешних Python зависимостей.

## Анализ актуального установленного комплекта из четырёх APK

При успешном резервном копировании с телефона уже известен путь
`C:\REA\Project\DollarFix\reverse\input\DollarFix-installed-20261122_112739`.

Исследовательский скрипт **не требует перемещать эти файлы в Git-репозиторий**. Вызови:

    git -C C:\REA\Project\DollarFix\research-tooling pull --ff-only

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\REA\Project\DollarFix\research-tooling\scripts\Setup-DollarFix-Tools.ps1 -ProjectRoot C:\REA\Project\DollarFix

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\REA\Project\DollarFix\research-tooling\scripts\Analyze-DollarFix-Snapshot.ps1 -ProjectRoot C:\REA\Project\DollarFix -SnapshotDirectory C:\REA\Project\DollarFix\reverse\input\DollarFix-installed-20261122_112739 -SkipInventory

JADX 1.5.7 и Apktool 3.0.3 загружаются из официальных выпусков GitHub с проверкой SHA-256. Нужна Java 17+; REA Doctor может остаться неуспешным из-за необязательных движков — причины смотри в отчёте.

Исправленный Codex запускается **из Git-клона `research-tooling`**, не из родительского каталога DollarFix (поэтому ошибка `Not inside a trusted directory` больше не должна возникать). Для него используется sandbox `workspace-write`, а дополнительная запись разрешена только в каталоги `reverse/work` и `reverse/reports`. Каталог сохранённых оригинальных APK остаётся вне разрешённых для записи директорий.

Опция `-SkipInventory` всё равно сверяет сохранённые APK по длине и SHA-256, но не проводит повторно прежнюю ZIP/ELF инвентаризацию.

Обязательно проверь `tool-status.json`: `exit_code = 0` для Codex, JADX и Apktool, а также физическое наличие соответствующих отчётов. REA `doctor` с кодом 1 означает необходимость изучить подробный отчёт, а не отсутствие всех REA-возможностей.
