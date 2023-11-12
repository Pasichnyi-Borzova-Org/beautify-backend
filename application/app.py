from flask import Flask
import user_blueprints
import appointment_blueprints

app = Flask(__name__)
app.register_blueprint(user_blueprints.blueprint)
app.register_blueprint(appointment_blueprints.blueprint)


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    return "Successful Connection"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
