import os
import json

from flask import Flask, render_template, request, redirect, url_for, make_response
from requests_oauthlib import OAuth2Session

try:
    import secrets  # needed only for localhost
except ImportError as ex:
    pass

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/github/login")
def github_login():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"))
    authorization_url, state = github.authorization_url("https://github.com/login/oauth/authorize")

    response = make_response(redirect(authorization_url))
    response.set_cookie("oauth_session", state, httponly=True)

    return response


@app.route("/github/callback")
def github_callback():
    github = OAuth2Session(os.getenv("GITHUB_CLIENT_ID"), state=request.cookies.get("oauth_state"))
    token = github.fetch_token("https://github.com/login/oauth/access_token",
                               client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
                               authorization_response=request.url)

    response = make_response(redirect(url_for("profile")))
    response.set_cookie("oauth_token", json.dumps(token), httponly=True)

    return response


@app.route("/profile")
def profile():
    token = json.loads(request.cookies.get("oauth_token"))
    github = OAuth2Session(os.getenv("GITHUB_CLIENT_ID"), token=token)

    profile_data = github.get("https://api.github.com/user").json()

    return render_template("profile.html", profile_data=profile_data)


@app.route("/github/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("oauth_token", expires=0)

    return response


if __name__ == "__main__":
    app.run(use_reloader=True)