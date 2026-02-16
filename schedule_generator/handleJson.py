import json

# ============
# Load JSON
# ============
with open("data2.json", "r", encoding="utf-8") as f:
    d2 = json.load(f)

tables = d2["r"]["dbiAccessorRes"]["tables"]


def get_table(name, cols=None):
    """
    Find a table by its name (and optionally by its data_columns).
    """
    if cols is None:
        for t in tables:
            if t["def"]["name"] == name:
                return t
        raise KeyError(f"Table not found: {name}")

    for t in tables:
        if t["def"]["name"] == name and t.get("data_columns") == cols:
            return t
    raise KeyError(f"Table not found: {name} with columns {cols}")


# ============
# Build lookup dicts by id
# ============
subjects = {r["id"]: r for r in get_table("Subjects")["data_rows"]}
teachers = {r["id"]: r for r in get_table("Teachers")["data_rows"]}
classes = {r["id"]: r for r in get_table("Classes")["data_rows"]}
classrooms = {r["id"]: r for r in get_table("Classrooms")["data_rows"]}
groups = {r["id"]: r for r in get_table("Groups")["data_rows"]}
lessons = {r["id"]: r for r in get_table("Lessons")["data_rows"]}
cards = get_table("Cards")["data_rows"]

# Periods table uses "period" as the key, not "id"
periods = {str(r["period"]): r for r in get_table("Periods")["data_rows"]}

# Days names (columns)
days_rows = get_table("Days", ["name", "short"])["data_rows"]
days_rows = sorted(days_rows, key=lambda x: int(x["id"]))  # keep Mon..Fri order
day_names = [d["name"] for d in days_rows]  # ["Понеделник", "Вторник", ...]
days_dict = {value: i for i, value in enumerate(day_names)}


# ============
# Helpers
# ============
def decode_days(bitstr: str):
    bitstr = (bitstr or "").strip()
    return [day_names[i] for i, ch in enumerate(bitstr) if ch == "1" and i < len(day_names)]


def time_range(start_period, duration):
    """
    Safe time range builder.
    Skips empty/invalid start periods.
    """
    sp = str(start_period).strip()
    if not sp.isdigit():
        return ""

    start = periods.get(sp)
    if not start:
        return ""

    dur = int(duration) if str(duration).strip().isdigit() else 1
    end_period = str(int(sp) + max(dur - 1, 0))
    end = periods.get(end_period, start)

    return f"{start['starttime']}–{end['endtime']}"


def extract_periods(start, length):
    start = int(start)
    length = int(length)
    return [p for p in range(start, start + length)]

    # ============
    # Extract schedule rows (human readable)
    # ============

rows = []

for c in cards:
        period = str(c.get("period", "")).strip()
        days = str(c.get("days", "")).strip()

        # IMPORTANT: skip cards that are not placed on timetable
        if not period.isdigit() or not days:
            continue

        lesson = lessons.get(c.get("lessonid"))
        if not lesson:
            continue

        duration = int(lesson.get("durationperiods", 1) or 1)

        subj = subjects.get(lesson.get("subjectid"), {})
        subject_name = subj.get("name", lesson.get("subjectid", ""))

        teacher_ids = lesson.get("teacherids", []) or []
        teacher_names = " / ".join(teachers.get(tid, {}).get("short", tid) for tid in teacher_ids)

        class_ids = lesson.get("classids", []) or []
        class_names = "; ".join(classes.get(cid, {}).get("name", cid) for cid in class_ids)

        group_ids = lesson.get("groupids", []) or []
        group_names = "; ".join(groups.get(gid, {}).get("name", gid) for gid in group_ids)

        room_ids = c.get("classroomids", []) or []
        room_names = ", ".join(classrooms.get(rid, {}).get("short", rid) for rid in room_ids)

        rows.append({
            "Day": ", ".join(decode_days(days)),
            "Day code": days_dict[", ".join(decode_days(days))],
            "Start period": int(period),
            "Duration (periods)": duration,
            "Time": time_range(period, duration),
            "Periods": extract_periods(period, duration),
            "Subject": subject_name,
            "Teachers": teacher_names,
            "Classes": class_names,
            # "Groups": group_names,
            "Classrooms": room_names,
            # "Card ID": c.get("id", ""),
            # "Lesson ID": c.get("lessonid", ""),
        })
