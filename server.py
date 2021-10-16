from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("./pages/index.html")


@app.route('/centrala')
def hq():
    return render_template("./pages/hq.html")


@app.route('/prodejny')
def stores():
    return render_template("./pages/stores.html")


@app.route('/sklady')
def warehouses():
    return render_template("./pages/warehouses.html")


if __name__ == "__main__":
    app.run()
