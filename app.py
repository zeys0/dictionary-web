import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, jsonify, redirect
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


app = Flask(__name__)


dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]


@app.route("/")
def main():
    words_result = db.words.find({}, {"_id": False})
    words = []
    for word in words_result:
        definition = word["definitions"][0]["shortdef"]
        definition = definition if type(definition) is str else definition[0]
        words.append(
            {
                "word": word["word"],
                "definition": definition,
            }
        )
    msg = request.args.get("msg")
    return render_template("index.html", words=words, msg=msg)


@app.route("/error")
def error_msg():
    msg = request.args.get("msg")
    second_msg = "Here are some suggested words"
    defs = request.args.get("definitions")

    if not defs:
        return render_template("msg.html", msg=msg)
    if defs:
        defs_list = defs.split()
        return render_template(
            "msg.html", msg=msg, defs=defs_list, second_msg=second_msg
        )


@app.route("/detail/<keyword>")
def detail(keyword):
    key_url = "bc908401-54d8-4b32-ac5f-c0c54c22445b"
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={key_url}"
    response = requests.get(url)
    definitions = response.json()
    status = request.args.get("status_give", "new")

    if not definitions:
        return redirect(
            url_for("error_msg", msg=f'Your word, "{keyword}" Could not be found ')
        )

    if type(definitions[0]) is str:
        definitions_str = " ".join(definitions)
        print(definitions)
        return redirect(
            url_for(
                "error_msg",
                msg=f"Your word {keyword}, Could not be found",
                definitions=definitions_str,
            )
        )
    return render_template(
        "detail.html", word=keyword, definitions=definitions, status=status
    )


@app.route("/api/save_word", methods=["POST"])
def save_word():
    json_data = request.get_json()
    word = json_data.get("word_give")
    definitions = json_data.get("definitions_give")
    date_now = datetime.now().strftime("%Y-%d-%m")
    doc = {"word": word, "definitions": definitions, "date": date_now}
    db.words.insert_one(doc)
    return jsonify({"result": "success", "msg": f"the word {word}, was saved"})


@app.route("/api/delete_word", methods=["POST"])
def delete_word():
    word_delete = request.form.get("word")
    db.words.delete_one({"word": word_delete})
    db.examples.delete_many({"word": word_delete})
    return jsonify({"result": "success", "msg": f"the word {word_delete}, was delete"})


@app.route("/api/get_exs", methods=["GET"])
def get_exs():
    word = request.args.get("word")
    example_data = db.examples.find({"word": word})
    examples = []
    for example in example_data:
        examples.append(
            {"example": example.get("example"), "id": str(example.get("_id"))}
        )
    return jsonify({"result": "success", "examples": examples})


@app.route("/api/save_ex", methods=["POST"])
def save_ex():
    word = request.form.get("word")
    example = request.form.get("example")
    doc = {"word": word, "example": example}
    db.examples.insert_one(doc)
    return jsonify(
        {
            "result": "success",
            "msg": f"yout example, {example}, for the {word}, was saved",
        }
    )


@app.route("/api/delete_ex", methods=["POST"])
def delete_ex():
    id = request.form.get("id")
    word = request.form.get("word")
    db.examples.delete_one({"_id": ObjectId(id)})

    return jsonify(
        {"result": "success", "msg": f"your example for the , {word}, was deleted "}
    )


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
