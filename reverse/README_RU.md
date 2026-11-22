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
