import os

def tool_calculator(expression):
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression) <= allowed:
            return "Ошибка: недопустимые символы"
        return str(eval(expression))
    except Exception as e:
        return f"Ошибка: {e}"

def tool_read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Ошибка: {e}"

def tool_write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Записано в {path}"
    except Exception as e:
        return f"Ошибка: {e}"

def tool_web_search(query):
    return f"[Заглушка] Результаты поиска по запросу: '{query}'. В реальном режиме здесь был бы ответ от поискового API."

def agent(task):
    print(f"\n{'='*60}")
    print(f"Задача: {task}")
    print(f"{'='*60}")

    if "15%" in task and "200" in task:
        print("Мысль: нужно посчитать 15% от 200.")
        result = tool_calculator("200 * 0.15")
        print(f"Действие: calculator('200 * 0.15') -> {result}")
        print("Мысль: нужно записать результат в файл.")
        write_result = tool_write_file("results/answer.txt", f"15% от 200 = {result}")
        print(f"Действие: write_file('results/answer.txt') -> {write_result}")
        print(f"Ответ: 15% от 200 = {result}. Результат записан в results/answer.txt.")

    elif "прочитай" in task.lower() and "input.txt" in task:
        print("Мысль: нужно прочитать файл data/input.txt.")
        content = tool_read_file("data/input.txt")
        print(f"Действие: read_file('data/input.txt') -> {content[:50]}...")
        print("Мысль: нужно посчитать количество слов.")
        words = len(content.split())
        print(f"Ответ: в файле {words} слов.")

    elif "курс" in task.lower() and "доллара" in task.lower():
        print("Мысль: нужен веб-поиск.")
        result = tool_web_search("курс доллара")
        print(f"Действие: web_search('курс доллара') -> {result}")
        print(f"Ответ: {result}")

    else:
        print("Мысль: задача не распознана в демо-режиме.")
        print("Ответ: не могу выполнить задачу в демо-режиме.")

if __name__ == "__main__":
    tasks = [
        "Посчитай 15% от 200 и запиши результат в файл.",
        "Прочитай файл data/input.txt и посчитай количество слов.",
        "Найди в интернете курс доллара.",
    ]
    for t in tasks:
        agent(t)
