echo "=== Запуск тестов доменного слоя ==="
python -m pytest tests/domain -v

echo -e "\n=== Запуск тестов application слоя ==="
python -m pytest tests/application -v

echo -e "\n=== Проверка типизации ==="
mypy domain application --strict

echo -e "\n=== Проверка стиля кода ==="
flake8 domain application tests