#TODO: автоматизировать is_odd_week

import openpyxl
import re
import pickle

__version__ = "0.0.9b"

WORKBOOK1 = openpyxl.load_workbook("all.xlsx")
WORKBOOK2 = openpyxl.load_workbook("correction.xlsx")

FILENAME_DATA = "data.pickle"

PATTERN_GROUP = "^[0-9][А-Я]{1,3}[0-9]+$"
PATTERN_ONE_TEACHER = r"(.*)\s([А-Я][а-я]+(-[А-Я][а-я]+)?\s+[А-Я][. ]*[А-Я][. ]*)"
PATTERN_TWO_TEACHERS = r"(.*)\s([А-Я][а-я]+(-[А-Я][а-я]+)?\s+[А-Я][. ]*[А-Я][. ]*)\s+([А-Я][а-я]+(-[А-Я][а-я]+)?\s+[А-Я][. ]*[А-Я][. ]*)"

is_odd_week = True

data = {}
try:
    with open(FILENAME_DATA, "rb") as file:
        data = pickle.load(file)
except FileNotFoundError:
    pass


def get_subject_teacher(string) -> list:
    match = re.search(PATTERN_TWO_TEACHERS, string)
    if match:
        subject = match.group(1)
        teacher1 = match.group(2)
        teacher2 = match.group(4)
        return subject, [teacher1, teacher2]
    
    match = re.search(PATTERN_ONE_TEACHER, string)
    if match:
        subject = match.group(1)
        teacher = match.group(2)
        return subject, [teacher]


    return None


def get_shedule(wb) -> dict:
    schedule = {}
    for sheet in wb.worksheets:
        for row in sheet.rows:
            for cell in filter(lambda x: isinstance(x.value, str) and re.match(PATTERN_GROUP, x.value), row):
                group = cell.value
                schedule[group] = []
                col_num = cell.column
                for row_num in range(cell.row+1, sheet.max_row + 1, 2):
                    merged_range = None
                    for r in sheet.merged_cells.ranges:
                        if sheet.cell(row=row_num, column=col_num).coordinate in r: 
                            merged_range = r
                            break

                    # Если ячейка не объедененная (т.е. пара чередуется) и неделя нечетная, 
                    # то смещает строку на 1 (выбираем 2 ячейку)
                    
                    week = (not merged_range) * is_odd_week 

                    subject_teacher = sheet.cell(row=row_num + week, column=col_num).value 
                    classroom = sheet.cell(row=row_num + week, column=col_num+1).value

        
                    if subject_teacher:
                        subject_teacher = get_subject_teacher(subject_teacher)
                        classroom = [classroom] if len(subject_teacher[1]) == 1 else [classroom, sheet.cell(row=row_num+1, column=col_num+1).value] # используем sheet вместо ws
                        schedule[group].append({"subject": subject_teacher[0], "teachers": subject_teacher[1], "classrooms": classroom}) 
                    else:
                        schedule[group].append(None)
    
    return schedule


def convert_schedule_to_string(group, schedule) -> str:
    lessons = schedule.get(group)
    if not lessons:
        return "Error"
    
    # Удаляем None в конце
    while lessons and lessons[-1] is None:
        lessons.pop()

    string = ""
    for index, lesson in enumerate(lessons):
        if lesson:
            string += f"{index+1}. {lesson['subject']}"
            for sub_index, (teacher, classroom) in enumerate(zip(lesson['teachers'], lesson['classrooms']), start=1):
                string += f"\n{sub_index} подгруппа:" if len(lesson['teachers']) == 2 else ""
                string += f"\nПреподаватель: {teacher}\nАудитория: {classroom}\n"
        else: 
            string += f"{index+1}. Окно\n"
        
        string += "\n"
    
    return string

print(f"Расписание Таврички v {__version__}\n\n")
group = input("Введите группу: ")


if group not in data:
    shedule = get_shedule(WORKBOOK1)
    shedule.update(get_shedule(WORKBOOK2))

    with open(FILENAME_DATA, "wb") as file:
            pickle.dump(shedule, file)
    data = shedule

print(convert_schedule_to_string(group, data))

