from flask import Flask, request, render_template_string

app = Flask(__name__)

# Intentionally vulnerable: user input is injected directly into HTML
TEMPLATE = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Search</title></head>
  <body>
    <h1>Search results for: {{ query }}</h1>
    <div id="results">
      <!-- Vulnerable reflection -->
      <p>User input: {{ query }}</p>
    </div>
  </body>
</html>
"""

@app.route("/")
def index():
    q = request.args.get("q", "")
    # render_template_string with unescaped variable used to illustrate vulnerability
    return render_template_string(TEMPLATE, query=q)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

