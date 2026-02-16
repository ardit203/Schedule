import json
import http.server, socketserver, webbrowser
from handleJson import rows, days_dict


##################
# Helpers
################
def contains_class(target):
    split = target.split("; ")
    arr = [s for s in split if s in target_classes]
    return len(arr) > 0


def contains_subject(target):
    base = target.split(" (", 1)[0].strip()
    return base in target_subjects


def add_color_and_short_name(target):
    for cl in target:
        split = cl['Subject'].split(" (", 1)
        base = split[0].strip()
        add = split[1].strip()
        cl['Color'] = target_subjects[base]['Color']
        cl['Short name'] = target_subjects[base]['Short name'] + " (" + add

    return target


# Study Programs -- change to your choice
target_classes = [
    "2г-ССП",

    "3г-ПИТ",
    "4г-ПИТ",

    "3г-ИМБ",
    "4г-ИМБ",

    "3г-КН",

    "3г-СИИС",
    "4г-СИИС",

    "3y-SEIS",
    "4y-SEIS",
]

# classes that will appear with their color in the schedule
target_main_classes = [
    "3y-SEIS",
    "4y-SEIS",
    # "4г-ПИТ",
]

# Subjects -- change to your choice
target_subjects = {
    "Управување со ИКТ проекти": {"Color": "#B7B369", "Short name": "IKT"},  # IKT
    "Интегрирани системи": {"Color": "#C667E5", "Short name": "IS"},  # IS
    "Електронска и мобилна трговија": {"Color": "#D79F62", "Short name": "EMT"},  # EMT
    "Континуирана интеграција и испорака": {"Color": "#8DC075", "Short name": "DevOps"},  # DevOps
    "Виртуелна реалност": {"Color": "#4845CA", "Short name": "VR"},  # VR,
    "Мобилни апликации": {"Color": "#539DCC", "Short name": "MA"},  # MA
}

# Labs -- Place for labs, later
target_labs = [
    {
        "Day": "Понеделник",
        "Day code": 0,
        "Start period": 2,
        "Duration (periods)": 2,
        "Time": "10:00-11:45",
        "Periods": [2, 3],
        "Subject": "Интегрирани системи (лаб)",
        "Classrooms": "Лаб 215",
    },
    {
        "Day": "Вторник",
        "Day code": 1,
        "Start period": 11,
        "Duration (periods)": 2,
        "Time": "18:00-19:45",
        "Periods": [11, 12],
        "Subject": "Мобилни апликации (лаб)",
        "Classrooms": "Лаб 2",
    }
]

if __name__ == '__main__':
    # Data filtered based on study program and subjects

    data = sorted([obj for obj in rows if contains_subject(obj['Subject'])],
                  key=lambda s: (s['Day code'], s['Start period']))

    print(target_classes)
    data = sorted([obj for obj in data if contains_class(obj['Classes'])],
                  key=lambda s: (s['Day code'], s['Start period']))

    data.extend(target_labs)

    data = add_color_and_short_name(data)

    data = {
        "days": days_dict,
        "main_classes": target_main_classes,
        "data": data
    }

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    PORT = 9999
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        httpd.serve_forever()
