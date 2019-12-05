from flask import Flask, render_template, url_for, request
import pandas as pd
import gensim
from rake_nltk import Rake
import ast

app = Flask(__name__)

app_data = pd.read_csv("../data/features_appstore_games.csv")
app_data = app_data.loc[app_data["user_rating_count"] > 0]
top_apps = app_data.sort_values("user_rating_count", ascending = False)[:10]
top_apps = top_apps.to_dict('records')

def keyword_func(combo_text):
    r = Rake()
    r.extract_keywords_from_text(combo_text)
    key_words_dict = r.get_word_degrees()
    return list(key_words_dict.keys())

model = gensim.models.KeyedVectors.load_word2vec_format('../../../Gensim/lexvec.enwiki+newscrawl.300d.W.pos.vectors')

def evaluator(df, title, description):
    new_app_combo = title + " " + description
    new_app_combo = new_app_combo.lower()
    new_app_keyw = keyword_func(new_app_combo)
    new_app_keyw_f = []
    for w in new_app_keyw:
        new_app_words = list(filter(lambda x: x in model.vocab, w))
        new_app_words = "".join(new_app_words)
        new_app_keyw_f.append(new_app_words)
    for empty_str in range(new_app_keyw_f.count("")):
        new_app_keyw_f.remove("")
    for w in new_app_keyw_f:
        if w in model.vocab:
            pass
        else:
            new_app_keyw_f.remove(w)
    word2vec_list = []
    for tup in model.most_similar(new_app_keyw_f):
            word, sim = tup
            word2vec_list.append(word)
    word2vec_list.extend(new_app_keyw_f)
    print(word2vec_list)
    app_title_list = []
    t_perc = 0.9
    threshold = round(t_perc * len(word2vec_list))
    print(f"The threshold is set to {t_perc} similarity, taking {threshold} words of {len(word2vec_list)}")
    t_perc_min = 0.25
    while len(app_title_list) < 5 and threshold > round(t_perc_min * len(word2vec_list)):
        for app in df.loc[df['keywords'].map(lambda x:sum(1 for w in word2vec_list if w in x))>=threshold,'id']:
            app_title_list.append(app)
        for item in app_title_list:
            if app_title_list.count(item) > 1:
                app_title_list.reverse()
                app_title_list.remove(item)
                app_title_list.reverse()
        print(f"There are {len(app_title_list)} at a {threshold} threshold")
        threshold -= round(0.05 * len(word2vec_list))
        print(len(app_title_list))
    return app_title_list[:10] if len(app_title_list) > 0 else print('No Results!')

def avg_rating_func(df, id_list):
    rating_avg = 0
    for i in range(len(id_list)):
        num = float(df.loc[df["id"] == id_list[i], "average_user_rating"])
        rating_avg += num
    rating_avg = rating_avg/len(id_list)
    return rating_avg

def avg_age_rate(df, id_list):
    age_avg = 0
    for i in range(len(id_list)):
        age = int(str(df.loc[df["id"] == id_list[i], "age_rating"]).split("    ")[1].split("\n")[0].replace("+", ""))
        age_avg += age
    age_avg = age_avg/len(id_list)
    if age_avg < 7.5:
        age_avg = "4+"
    elif age_avg < 10.5:
        age_avg = "9+"
    elif age_avg < 14.5:
        age_avg = "12+"
    else:
        age_avg = "17+"
    return age_avg

def genre_app(df, id_list):
    gen_list = []
    for i in range(len(id_list)):
        gen = str(df.loc[df["id"] == id_list[i], "primary_genre"]).split("    ")[1].split("\n")[0]
        if gen in gen_list:
            pass
        else:
            gen_list.append(gen)
    return gen_list

def eval_literal(list_words):
    try:
        return ast.literal_eval(list_words)
    except ValueError:
        return ast.literal_eval(str(list_words))

def app_categ(df, id_list):
    categ_list = []
    for i in range(len(id_list)):
        for elem in list(df.loc[df["id"] == id_list[i], "categories"])[0]:
            if elem in categ_list:
                pass
            else:
                categ_list.append(elem)
    return categ_list

def app_price(df, id_list):
    zero_count = 0
    price_avg = 0
    max_price = 0
    for i in range(len(id_list)):
        price = float(df.loc[df["id"] == id_list[i], "price"])
        if price == 0:
            zero_count += 1
        if price > max_price:
            max_price = price
        price_avg += price
    price_avg = price_avg/len(id_list)
    zero_count = (zero_count/len(id_list))*100
    return price_avg, zero_count, max_price

@app.route('/')
def home_page():
    return render_template("home.html", top_apps=top_apps)

@app.route("/evaluation", methods = ["POST"])
def eval():
    title = request.form['appTitle']
    desc = request.form['appDesc']
    df = pd.read_csv("../data/features_appstore_games.csv")
    df = df.loc[df["user_rating_count"] > 0]
    df['categories'] = df['categories'].map(eval_literal)
    sim_app_list = evaluator(df, title, desc)
    eval_df = pd.DataFrame()
    rating_avg = avg_rating_func(df, sim_app_list)
    age_avg = avg_age_rate(df, sim_app_list)
    genre_list = genre_app(df, sim_app_list)
    category_list = app_categ(df, sim_app_list)
    price_avg, free_apps, max_price = app_price(df, sim_app_list)
    if len(genre_list) == 1:
        def_genre = 1
    else:
        def_genre = 0
    for i in range(len(sim_app_list)):
        if i == 0:
            eval_df = df.loc[df["id"] == sim_app_list[i]]
        else:
            app = df.loc[df["id"] == sim_app_list[i]]
            eval_df = pd.concat([eval_df, app])
    eval_df = eval_df.to_dict('records')
    return render_template("evaluation.html", evalT = title, evalD = desc, the_list = eval_df, avg_rate = rating_avg, age_avg = age_avg, gen_app = genre_list, genre_def = def_genre, categ_list = category_list, price_avg = price_avg, app_free = free_apps, max_price = max_price)

if __name__ == "__main__":
    app.run(debug = True)
