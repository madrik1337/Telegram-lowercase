import re
import os
import glob
from pathlib import Path


# Кастомные значения для английского языка (EN)
CUSTOM_VALUES_EN = {
    'ios': {
        "Notification.StarsGiftOffer.Offer": 'the user offered you %2$@ for your gift %3$@',
        "Notification.StarGiftOffer.Offer": 'the user offered you **%2$@** for your gift **%3$@**.',
    },
    'android': {
        "GiftOfferOfferedTextStars": 'offered you **%2$s stars** for **%3$s**.\\n\\n\\nname user: %1$s',
        "GiftOfferOfferedTextTON": 'offered you **%2$s ton** for **%3$s**.\\n\\n\\nname user: %1$s',
    },
    'tdesktop': {
        "lng_action_gift_offer": 'offered you {cost} for {name}.\\n\\n\\nname user: {user}',
    },
    'macos': {
        "Chat.Service.Offer.ReceivedOffer": 'offered you **%2$@** for your gift **%3$@**.\\n\\n\\nname user: %1$@',
    },
}

# Кастомные значения для русского языка (RU)
# Здесь можно добавить свои значения для русских файлов
CUSTOM_VALUES_RU = {
    'ios': {
        "Notification.StarsGiftOffer.Offer": 'пользователь предлагает Вам %2$@ за подарок %3$@',
        "Notification.StarGiftOffer.Offer": 'пользователь предлагает Вам **%2$@** за подарок **%3$@**.',
    },
    'android': {
        "GiftOfferOfferedTextStars": 'предлагает Вам **%2$s stars** за **%3$s**.\\n\\n\\nимя пользователя: %1$s',
        "GiftOfferOfferedTextTON": 'предлагает Вам **%2$s ton** за **%3$s**.\\n\\n\\nимя пользователя: %1$s',
    },
    'tdesktop': {
        "lng_action_gift_offer": 'предлагает Вам {cost} за {name}.\\n\\n\\nимя пользователя: {user}',
    },
    'macos': {
        "Chat.Service.Offer.ReceivedOffer": 'предлагает Вам **%2$@** за подарок **%3$@**.\\n\\n\\nимя пользователя: %1$@',
    },
}

# Кастомные значения для украинского языка (UA/UK)
# Здесь можно добавить свои значения для украинских файлов
CUSTOM_VALUES_UA = {
    'ios': {
        "Notification.StarsGiftOffer.Offer": "користувач пропонує вам %2$@ за %3$@",
        "Notification.StarGiftOffer.Offer": "користувач пропонує вам **%2$@** за **%3$@**.",
    },
    'android': {
        "GiftOfferOfferedTextStars": "пропонує вам **%2$s stars** за **%3$s**.\\n\\n\\nім'я користувача: %1$s",
        "GiftOfferOfferedTextTON": "пропонує вам **%2$s ton** за **%3$s**.\\n\\n\\nім'я користувача: %1$s",
    },
    'tdesktop': {
        "lng_action_gift_offer": "пропонує вам {cost} за {name}.\\n\\n\\nім'я користувача: {user}",
    },
    'macos': {
        # Пример: "Some.Key": "якесь значення",
    },
}


def lowercase_strings_file(content, custom_values=None):
    """
    Преобразует ВСЕ буквы в значениях .strings файла в нижний регистр.
    
    Формат: "key" = "Value";
    
    Args:
        content: содержимое файла
        custom_values: словарь {ключ: значение} для автоматической замены
    """
    if custom_values is None:
        custom_values = {}
    
    lines = content.split('\n')
    modified_lines = []
    count = 0
    
    for line in lines:
        # Ищем строки формата "lng_..." = "Value..."
        match = re.match(r'^("(.*?)"\s*=\s*")(.+)(";)\s*$', line)
        
        if match:
            key = match.group(2)
            value = match.group(3)
            
            # Проверяем, есть ли кастомное значение для этого ключа
            if key in custom_values:
                new_line = match.group(1) + custom_values[key] + match.group(4)
                modified_lines.append(new_line)
            else:
                new_line = match.group(1) + value.lower() + match.group(4)
                modified_lines.append(new_line)
            count += 1
        else:
            modified_lines.append(line)
    
    return '\n'.join(modified_lines), count


def lowercase_xml_file(content, custom_values=None):
    """
    Преобразует ВСЕ буквы в значениях .xml файла в нижний регистр.
    
    Формат: <string name="Key">Value</string>
    
    Исключения: строки с определёнными именами (форматы дат, и т.д.)
    
    Args:
        content: содержимое файла
        custom_values: словарь {string_name: значение} для автоматической замены
    """
    if custom_values is None:
        custom_values = {}
    # Список паттернов для исключений (по string name)
    exclude_patterns = [
        r'^formatter',           # formatterBoostExpired, formatterMonth, и т.д.
        r'^format',              # formatDateAtTime, formatDateSchedule, и т.д.
        r'^chat.*Date',          # chatDate, chatFullDate
        r'^Send.*At$',           # SendTodayAt, SendDayAt, и т.д.
        r'^Start.*At$',          # StartTodayAt, StartDayAt, и т.д.
        r'^Starts.*At$',         # StartsTodayAt, StartsDayAt, и т.д.
        r'^Publish.*At$',        # PublishTodayAt, PublishDayAt, и т.д.
        r'^Remind.*At$',         # RemindTodayAt, RemindDayAt, и т.д.
    ]
    
    lines = content.split('\n')
    modified_lines = []
    count = 0
    
    for line in lines:
        # Ищем строки формата <string name="...">Value</string>
        match = re.match(r'^(\s*<string\s+name="([^"]+)">)(.+)(</string>)\s*$', line)
        
        if match:
            string_name = match.group(2)
            value = match.group(3)
            
            # Проверяем, есть ли кастомное значение для этого string name
            if string_name in custom_values:
                new_line = match.group(1) + custom_values[string_name] + match.group(4)
                modified_lines.append(new_line)
                continue
            
            # Проверяем наличие CDATA блоков
            cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
            cdata_blocks = re.findall(cdata_pattern, value)
            has_cdata = len(cdata_blocks) > 0
            
            # Проверяем, нужно ли исключить эту строку
            should_exclude = any(re.search(pattern, string_name) for pattern in exclude_patterns)
            
            if should_exclude:
                # Для исключённых строк:
                # 1. Добавляем :ss после :mm
                modified_value = value.replace(':mm', ':mm:ss')
                # 2. Преобразуем в lowercase только текст внутри \'...\'
                modified_value = re.sub(
                    r"\\'([^']+)\\'",
                    lambda m: "\\'" + m.group(1).lower() + "\\'",
                    modified_value
                )
                new_line = match.group(1) + modified_value + match.group(4)
                modified_lines.append(new_line)
            elif has_cdata:
                # Если есть CDATA, преобразуем в lowercase весь текст, включая содержимое CDATA
                # но сохраняем теги <![CDATA[ и ]]> без изменений
                
                # Сначала заменяем CDATA блоки на уникальные плейсхолдеры
                temp_value = value
                placeholders = []
                for i, match_obj in enumerate(re.finditer(cdata_pattern, value)):
                    cdata_content = match_obj.group(1)
                    # Преобразуем содержимое CDATA в lowercase
                    lowercased_cdata = f"<![CDATA[{cdata_content.lower()}]]>"
                    # Используем плейсхолдер только из цифр и подчеркиваний - без букв
                    placeholder = f"___99999_{i}_99999___"
                    placeholders.append((placeholder, lowercased_cdata))
                    temp_value = temp_value.replace(match_obj.group(0), placeholder, 1)
                
                # Преобразуем весь оставшийся текст в lowercase
                temp_value = temp_value.lower()
                
                # Возвращаем CDATA блоки (уже с lowercase содержимым)
                for placeholder, cdata_block in placeholders:
                    temp_value = temp_value.replace(placeholder, cdata_block)
                
                new_line = match.group(1) + temp_value + match.group(4)
                modified_lines.append(new_line)
                count += 1
            else:
                # Преобразуем в lowercase
                new_line = match.group(1) + value.lower() + match.group(4)
                modified_lines.append(new_line)
                count += 1
        else:
            modified_lines.append(line)
    
    return '\n'.join(modified_lines), count


def process_file(input_path, output_path):
    """
    Обрабатывает один файл в зависимости от его расширения.
    """
    file_ext = Path(input_path).suffix.lower()
    filename = os.path.basename(input_path)
    
    # Определяем язык файла
    lang_code = extract_language_code(filename)
    
    # Определяем платформу
    platform = None
    if filename.startswith('ios'):
        platform = 'ios'
    elif filename.startswith('android'):
        platform = 'android'
    elif filename.startswith('tdesktop'):
        platform = 'tdesktop'
    elif filename.startswith('macos'):
        platform = 'macos'
    
    # Выбираем словарь кастомных значений на основе языка и платформы
    custom_values = None
    if lang_code == 'en' and platform:
        custom_values = CUSTOM_VALUES_EN.get(platform, {})
    elif lang_code == 'ru' and platform:
        custom_values = CUSTOM_VALUES_RU.get(platform, {})
    elif lang_code == 'uk' and platform:
        custom_values = CUSTOM_VALUES_UA.get(platform, {})
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_ext == '.strings':
            new_content, count = lowercase_strings_file(content, custom_values)
        elif file_ext == '.xml':
            new_content, count = lowercase_xml_file(content, custom_values)
        else:
            print(f"  ⚠ Неподдерживаемый формат: {file_ext}")
            return False
        
        # Создаём директорию если её нет
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        filename = os.path.basename(input_path)
        print(f"  ✓ {filename}: изменено строк: {count}")
        return True
        
    except Exception as e:
        print(f"  ✗ Ошибка при обработке {input_path}: {e}")
        return False


def extract_language_code(filename):
    """
    Извлекает код языка из имени файла.
    Примеры: android_ru_*.xml -> ru, ios_en_*.strings -> en
    """
    # Паттерн для извлечения кода языка: префикс_ЯЗЫК_версия.расширение
    match = re.search(r'_(ru|en|es|de|fr|it|pt|ja|ko|zh|ar|uk|tr|pl|id|nl|cs|sv|no|da|fi|el|th|vi|he|hi)_', filename)
    if match:
        return match.group(1)
    return None


def main():
    """
    Основная функция для обработки файлов из папки translations.
    Автоматически распределяет файлы по папкам в зависимости от языка.
    """
    # Папки
    source_dir = "translations"
    output_base_dir = "lowercase_translations"
    
    # Проверяем существование исходной папки
    if not os.path.exists(source_dir):
        print(f"❌ Папка '{source_dir}' не найдена!")
        print(f"Создаём папку '{source_dir}'...")
        os.makedirs(source_dir, exist_ok=True)
        print(f"✓ Поместите файлы tdesktop*.strings, ios*.strings, macos*.strings или android*.xml в папку '{source_dir}'")
        return
    
    # Паттерны для поиска файлов
    patterns = [
        os.path.join(source_dir, "tdesktop*.strings"),
        os.path.join(source_dir, "ios*.strings"),
        os.path.join(source_dir, "macos*.strings"),
        os.path.join(source_dir, "android*.xml")
    ]
    
    # Собираем все файлы
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern))
    
    if not all_files:
        print(f"❌ Файлы не найдены в папке '{source_dir}'")
        print(f"Ищем: tdesktop*.strings, ios*.strings, macos*.strings, android*.xml")
        return
    
    print(f"Обработка файлов из папки: {source_dir}")
    print("-" * 60)
    print(f"Найдено файлов: {len(all_files)}\n")
    
    # Обрабатываем каждый файл
    success_count = 0
    language_stats = {}
    
    for input_path in all_files:
        filename = os.path.basename(input_path)
        
        # Определяем язык из имени файла
        lang_code = extract_language_code(filename)
        
        if lang_code:
            # Создаём папку для конкретного языка
            output_dir = f"{output_base_dir}_{lang_code}"
            output_path = os.path.join(output_dir, filename)
            
            if process_file(input_path, output_path):
                success_count += 1
                language_stats[lang_code] = language_stats.get(lang_code, 0) + 1
        else:
            # Если язык не определён, сохраняем в общую папку
            output_dir = output_base_dir
            output_path = os.path.join(output_dir, filename)
            print(f"  ⚠ Не удалось определить язык для: {filename}")
            
            if process_file(input_path, output_path):
                success_count += 1
                language_stats['unknown'] = language_stats.get('unknown', 0) + 1
    
    print("\n" + "-" * 60)
    print(f"✓ Обработано файлов: {success_count}/{len(all_files)}")
    print(f"\nРаспределение по языкам:")
    for lang, count in sorted(language_stats.items()):
        if lang == 'unknown':
            print(f"  • {lang}: {count} файл(ов) → {output_base_dir}/")
        else:
            print(f"  • {lang}: {count} файл(ов) → {output_base_dir}_{lang}/")


if __name__ == "__main__":
    main()
