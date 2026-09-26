# Development Notes

## Reproduce the application

1. Use Python 3.10 or newer.
2. Install dependencies with `python3 -m pip install -r requirements.txt`.
3. Start the development server with `python3 app.py`.
4. Open `http://127.0.0.1:5000` in a browser.

## Implementation steps

1. Created a Flask route that renders the calculator and accepts keypad form submissions.
2. Added a server-side expression evaluator using Python's syntax tree, allowing only decimal numbers, parentheses, unary signs, addition, subtraction, multiplication, division, and bounded integer powers. No Python `eval` or browser JavaScript is used.
3. Added a responsive HTML/CSS keypad and display, retaining expression and answer state between requests.
4. Declared Flask in `requirements.txt` and documented the run steps above.

## Constraint note

HTML forms submitted to Flask cause a browser document navigation. With JavaScript prohibited, the page cannot update in place after every key press. The application keeps a consistent server-rendered layout and preserves calculator state, but eliminating those navigations requires relaxing the no-JavaScript requirement or changing the architecture.