from flask import Flask, render_template, request
import sqlite3
import enchant
import difflib


"""
@author Maxim Trofimov (tg: @trofik00777)
"""


app = Flask(__name__)


HOST = ""
MODULES = [["4a", ""],
           ["4b", ""],
           ["4c", ""],
           ["4d", ""],
           ["4e", ""],
           ["5a", ""],
           ["5b", ""],
           ["5c", ""],
           ["5d", ""],
           ["5e", ""],
           ["6a", ""],
           ["6b", ""],
           ["8a", ""],
           ["8b", ""]]
PATH = "db/WordList.db"


def get_word_for_trainer(modules: list):
    con = sqlite3.connect(PATH)
    cur = con.cursor()
    res = cur.execute(f"SELECT rus, en FROM word_list WHERE module IN ({', '.join(modules)}) ORDER BY RANDOM() LIMIT 1").fetchone()
    # print(res)
    return res


def search_word(masks: list):
    try:
        con = sqlite3.connect(PATH)
        cur = con.cursor()
        query = " AND ".join([f" rus LIKE '%{i.lower().strip()}%' " for i in masks])
        res = cur.execute(
            f"SELECT en, module FROM word_list WHERE {query} ORDER BY module").fetchall()
        # print(res)
        return res
    except:
        return ""


def search_any_words(queries):
    try:
        dictionary = enchant.Dict("ru")

        correct = []

        for query in queries:
            check = dictionary.check(query)

            if not check:
                sim = dict()

                suggestions = set(dictionary.suggest(query))

                for word in suggestions:
                    measure = difflib.SequenceMatcher(None, query, word).ratio()
                    sim[measure] = word

                correct.append(sim[max(sim.keys())])
            else:
                correct.append(query)

        return correct
    except:
        return False


@app.route('/')
def home_page():
    return render_template("index.html", name=HOST)


@app.route('/trainer')
def trainer_page(q=False, a=False, modules=False):
    if q and a:
        pass
    else:
        q = a = "Choose any module"
    if not modules:
        modules = MODULES[:]
    return render_template("trainer.html", name=HOST, question=q, answer=a, modules=modules)


@app.route('/trainer/', methods=['post', 'get'])
def continue_trainer():
    if request.method == 'POST':
        username = request.form.get('continue')  # запрос к данным формы
        mods = request.form.getlist('modules_select[]')
        # print(username, mods)
        mods_for_next_page = []
        for i in MODULES:
            if i[0] in mods:
                mods_for_next_page.append([i[0], "selected"])
            else:
                mods_for_next_page.append([i[0], ""])
        try:
            q, a = get_word_for_trainer([f"'{mod}'" for mod in mods])
        except:
            q = a = "Choose any module"

        return trainer_page(q=q, a=a, modules=mods_for_next_page)


@app.route('/assistant')
def assistant_page(answers=False, current_text=""):
    return render_template("assistant.html", name=HOST, answers=answers, current_text=current_text)


@app.route('/assistant/', methods=['post', 'get'])
def search_assistant():
    if request.method == 'POST':
        query = request.form.get('query')  # запрос к данным формы
        print(query)
        # print(enchant.list_languages())
        if query:
            queries = query.strip().split()

            answer = search_word(queries)
            if answer:
                answer = [f"{i[0]}   ({i[1]})" for i in answer]
            else:
                corr = search_any_words(queries)
                if corr:
                    answer = search_word(corr)
                    if answer:
                        answer = [f"Возможно, вы имели в виду: {' '.join(corr)}"] + [f"{i[0]}   ({i[1]})" for i in answer]
                    else:
                        answer = ["Nothing..."]
                else:
                        answer = ["Nothing..."]
        else:
            answer = []
        # print(answer)

        return assistant_page(answers=answer, current_text=query)


if __name__ == '__main__':
    app.run()
    # get_word_for_trainer(["'1a'"])
