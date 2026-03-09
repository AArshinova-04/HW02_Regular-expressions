from pprint import pprint
import csv
import re

# Читаем адресную книгу
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)
pprint(contacts_list)

# Отделяем заголовок от данных
header = contacts_list[0]
data = contacts_list[1:]

# Функция нормализации ФИО
def normalize_fullname(contact):
    # Первые три поля объединяем через пробел, убираем пустые части
    parts = [p for p in contact[:3] if p]
    full_name = ' '.join(parts)
    words = full_name.split()
    if len(words) == 3:
        last, first, surname = words
    elif len(words) == 2:
        last, first = words
        surname = ''
    elif len(words) == 1:
        last = words[0]
        first = surname = ''
    else:
        # Если что-то пошло не так, оставляем как есть
        last, first, surname = contact[:3]
    return [last, first, surname] + contact[3:]

# Функция приведения телефона к стандартному виду
def normalize_phone(phone):
    if not phone:
        return phone
    # Регулярное выражение для поиска основного номера и добавочного
    pattern = re.compile(
        r"(\+7|8)?\s*\(?(\d{3})\)?\s*[-\s]?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})"
        r"(?:\s*[\(\s]*(доб\.?\s*(\d+))[\)\s]*)?",
        flags=re.IGNORECASE
    )
    def repl(match):
        groups = match.groups()
        # Основной номер в формате +7(999)999-99-99
        main = f"+7({groups[1]}){groups[2]}-{groups[3]}-{groups[4]}"
        # Добавочный номер, если есть
        extra = groups[5]  # это группа "доб. 1234" целиком, но мы возьмём только цифры
        if groups[6]:  # группа только с цифрами добавочного номера
            main += f" доб.{groups[6]}"
        return main
    return pattern.sub(repl, phone)

# Применяем нормализацию ко всем записям
normalized_data = []
for contact in data:
    # Нормализуем ФИО
    contact = normalize_fullname(contact)
    # Нормализуем телефон (индекс 5)
    contact[5] = normalize_phone(contact[5])
    normalized_data.append(contact)

# Объединение дубликатов по фамилии и имени
merged_dict = {}
for contact in normalized_data:
    last, first = contact[0], contact[1]
    key = (last, first)
    if key not in merged_dict:
        merged_dict[key] = contact[:]  # копируем запись
    else:
        existing = merged_dict[key]
        # Для каждого поля (кроме фамилии и имени) берём непустое значение
        for i in range(2, len(contact)):
            if not existing[i] and contact[i]:
                existing[i] = contact[i]
            # Если оба непустые и разные – конфликт, оставляем существующее
            # (в представленных данных таких ситуаций нет)

# Получаем итоговый список записей
final_data = list(merged_dict.values())

# Добавляем заголовок обратно
final_list = [header] + final_data

# Сохраняем в новый CSV-файл
with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(final_list)

print('-'*30)
print("Адресная книга приведена в порядок! Результат записан в phonebook.csv")
print('-'*30)
#pprint(final_list)