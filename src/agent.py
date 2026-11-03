"""
Mini-Agent: ReAct + Reflexion (демо-режим, без API).
Опора: глава 6 книги «AI-инженерия» (Чип Хьюен).
"""

import os
import json
import statistics


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
    return f"[Заглушка] Результаты поиска по запросу: '{query}'."


TOOLS = {
    "calculator": tool_calculator,
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "web_search": tool_web_search,
}


def plan(task):
    t = task.lower()
    if "15%" in task and "200" in task:
        steps = [("calculator", {"expression": "200 * 0.15"})]
        if "запиши" in t or "файл" in t:
            steps.append(("write_file", {"path": "results/answer.txt", "content": "RESULT_PLACEHOLDER"}))
        return steps    
    if "прочитай" in t and "input.txt" in t:
        return [("read_file", {"path": "data/input.txt"})]
    if "курс" in t and "доллара" in t:
        return [("web_search", {"query": "курс доллара"})]
    return []


def reflect(task, steps_done, last_observation):
    t = task.lower()
    if not steps_done:
        return False, "План пуст — задача не распознана."
    if "15%" in task and "200" in task:
        if "write_file" in steps_done:
            return True, "Результат вычислен и записан."
        return False, "Результат не записан."
    if "input.txt" in t:
        if "read_file" in steps_done:
            return True, "Файл прочитан."
        return False, "Файл не прочитан."
    if "курс" in t:
        if "web_search" in steps_done:
            return True, "Поиск выполнен."
        return False, "Поиск не выполнен."
    return False, "Цель не достигнута."


def run_agent(task, max_steps=5, use_reflexion=True):
    trace = {
        "task": task,
        "steps": [],
        "invalid_tool_calls": 0,
        "claimed_done_but_not": 0,
        "done": False,
    }
    steps = plan(task)

    for step_num, (action, params) in enumerate(steps, 1):
        if step_num > max_steps:
            break
        trace["steps"].append({"thought": f"Шаг {step_num}: {action}", "action": action, "params": params})
        if action not in TOOLS:
            trace["invalid_tool_calls"] += 1
            trace["steps"][-1]["observation"] = f"Ошибка: инструмент '{action}' не существует"
            continue

        if action == "write_file" and params.get("content") == "RESULT_PLACEHOLDER":
            prev = trace["steps"][-2]["observation"] if len(trace["steps"]) >= 2 else "?"
            params = {**params, "content": f"15% от 200 = {prev}"}
        observation = TOOLS[action](**params)
        trace["steps"][-1]["observation"] = observation

        if use_reflexion:
            done, reason = reflect(task, [s["action"] for s in trace["steps"]], observation)
            trace["steps"][-1]["reflection"] = {"done": done, "reason": reason}
            if done:
                trace["done"] = True
                break
            if step_num == len(steps) and not done:
                trace["claimed_done_but_not"] += 1

    if not use_reflexion and trace["steps"]:
        trace["done"] = True
    return trace


def summarize_traces(traces):
    n = len(traces)
    successes = sum(1 for t in traces if t["done"])
    avg_steps = statistics.mean(len(t["steps"]) for t in traces) if traces else 0

    invalid = sum(t["invalid_tool_calls"] for t in traces)
    false_done = sum(t["claimed_done_but_not"] for t in traces)
    return {
        "tasks": n,
        "successes": successes,
        "success_rate": round(successes / n, 2) if n else 0,
        "avg_steps": round(avg_steps, 2),
        "invalid_tool_calls": invalid,
        "false_done": false_done,
    }

if __name__ == "__main__":
    tasks = [
        "Посчитай 15% от 200 и запиши результат в файл.",
        "Прочитай файл data/input.txt и посчитай количество слов.",
        "Найди в интернете курс доллара.",
        "Посчитай 15% от 200.",
        "Что такое квантовая физика?",
    ]
    os.makedirs("results", exist_ok=True)

    print("=" * 60)
    print("Агент БЕЗ рефлексии")
    print("=" * 60)
    traces_no = [run_agent(t, use_reflexion=False) for t in tasks]
    summary_no = summarize_traces(traces_no)
    print(json.dumps(summary_no, ensure_ascii=False, indent=2))

    print("=" * 60)
    print("Агент С рефлексией")
    print("=" * 60)
    traces_yes = [run_agent(t, use_reflexion=True) for t in tasks]
    summary_yes = summarize_traces(traces_yes)
    print(json.dumps(summary_yes, ensure_ascii=False, indent=2))

    with open("results/traces.json", "w", encoding="utf-8") as f:
        json.dump({"no_reflexion": traces_no, "with_reflexion": traces_yes}, f,
                  ensure_ascii=False, indent=2)
    with open("results/summary.txt", "w", encoding="utf-8") as f:
        f.write("Без рефлексии:\n" + json.dumps(summary_no, ensure_ascii=False, indent=2))
        f.write("\n\nС рефлексией:\n" + json.dumps(summary_yes, ensure_ascii=False, indent=2))
    print("\nРезультаты сохранены в results/traces.json и results/summary.txt")
