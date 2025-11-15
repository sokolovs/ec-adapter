# RU: 🔥 Интеграция ectoControl для Home Assistant

Интеграция предназначена для подключения адаптеров **ectoControl**, обеспечивающих управление газовыми и электрическими котлами по различным коммуникационным шинам. В зависимости от модели адаптера поддерживаются такие протоколы, как **eBUS**, **OpenTherm**, **Navien** и другие.

## Возможности

### ✔ Автоматическое создание сенсоров
Интеграция формирует сенсоры для всех **MODBUS-регистров чтения**, описанных в документации адаптера.
Это позволяет получать актуальные параметры работы котла — температуру в контурах, статус, расход и другие данные (зависит от модели котла) и и создавать собственные автоматизации на их основе.

### ✔ Создание элементов управления
Для всех **MODBUS-регистров записи** создаются соответствующие управляющие сущности (числовые регуляторы, селекторы и т. д.).
Это даёт возможность изменять параметры работы котла из Home Assistant и создавать собственные автоматизации с использованием данных сущностей.

### ✔ Мониторинг соединения с котлом
Интеграция отслеживает текущее состояние подключения адаптера к котлу и отображает соответствующий статус в Home Assistant.

### ✔ Автоматическая отправка необходимых параметров
При установлении соединения адаптера с котлом интеграция отправляет все требуемые параметры, обеспечивая корректный запуск и работу отопительного оборудования при перезапусках.

### ✔ Корректная работа после рестарта Home Assistant
После перезапуска Home Assistant интеграция отслеживает собственный запуск и повторно отправляет котлу необходимые значения для восстановления корректной работы.

---

# EN: 🔥 ectoControl Integration for Home Assistant

This integration connects **ectoControl** adapters that provide control of gas and electric boilers via various communication buses. Depending on the adapter model, supported protocols include **eBUS**, **OpenTherm**, **Navien**, and others.

## Features

### ✔ Automatic sensor creation
The integration generates sensors for all **MODBUS read registers** described in the adapter documentation.
This allows Home Assistant to receive up-to-date boiler parameters — such as circuit temperatures, system status, flow rate, and other values (depending on the boiler model) — and use them to build custom automations.

### ✔ Creation of control entities
For all **MODBUS write registers**, the integration creates corresponding control entities (numeric, selectors, etc.).
This makes it possible to adjust boiler parameters directly from Home Assistant and build automations using these entities.

### ✔ Monitoring of the boiler connection
The integration continuously monitors the connection status between the adapter and the boiler and exposes this status in Home Assistant.

### ✔ Automatic transmission of required parameters
When the adapter establishes a connection with the boiler, the integration automatically sends all required configuration parameters, ensuring proper boiler startup and operation during reconnections.

### ✔ Proper behavior after Home Assistant restarts
After Home Assistant restarts, the integration detects its own initialization and re-sends the necessary values to the boiler to restore correct operation.
