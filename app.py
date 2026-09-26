import ast
import operator
from decimal import Decimal, localcontext

from flask import Flask, render_template, request

app = Flask(__name__)

MAX_EXPRESSION_LENGTH = 120
MAX_RESULT_MAGNITUDE = 1000
MAX_EXPONENT = 999


class ExpressionEvaluator(ast.NodeVisitor):
    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def visit_Expression(self, node):
        return self._check_result(self.visit(node.body))

    def visit_Constant(self, node):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("Only numbers are allowed.")
        value = Decimal(str(node.value))
        if not value.is_finite():
            raise ValueError("That number is too large.")
        return self._check_result(value)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Pow):
            if right != right.to_integral_value() or abs(right) > MAX_EXPONENT:
                raise ValueError("Use a whole-number exponent from -999 to 999.")
            result = left**int(right)
        else:
            operation = self._binary_operators.get(type(node.op))
            if operation is None:
                raise ValueError("That operation is not supported.")
            result = operation(left, right)

        return self._check_result(result)

    def visit_UnaryOp(self, node):
        value = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("That operation is not supported.")

    def generic_visit(self, node):
        raise ValueError("Use numbers, parentheses, and basic operators only.")

    @staticmethod
    def _check_result(value):
        if not value.is_finite():
            raise ValueError("The result is too large.")
        if value and abs(value.adjusted()) > MAX_RESULT_MAGNITUDE:
            raise ValueError("The result is too large.")
        return value


def calculate(expression):
    if not expression or len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Enter an expression up to 120 characters.")

    normalized = expression.replace("^", "**")
    tree = ast.parse(normalized, mode="eval")
    with localcontext() as context:
        context.prec = 28
        result = ExpressionEvaluator().visit(tree)
    return format_result(result)


def format_result(value):
    if value == 0:
        return "0"
    formatted = format(value.normalize(), "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


@app.route("/", methods=["GET", "POST"])
def calculator():
    expression = ""
    answer = ""
    error = ""
    evaluated = False

    if request.method == "POST":
        expression = request.form.get("expression", "")[:MAX_EXPRESSION_LENGTH]
        answer = request.form.get("answer", "")
        evaluated = request.form.get("evaluated") == "true"
        action = request.form.get("action", "")

        if action == "clear":
            expression = ""
            answer = ""
            evaluated = False
        elif action == "delete":
            expression = expression[:-1]
            answer = ""
            evaluated = False
        elif action == "equals":
            try:
                answer = calculate(expression)
                evaluated = True
            except (ArithmeticError, SyntaxError, ValueError):
                answer = ""
                evaluated = False
                error = "Check the expression and try again."
        elif action in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "+", "-", "*", "/", "^", "(", ")"}:
            if evaluated and action not in {"+", "-", "*", "/", "^"}:
                expression = ""
            elif evaluated:
                expression = answer
            expression += action
            answer = ""
            evaluated = False

    return render_template(
        "index.html",
        expression=expression,
        answer=answer,
        error=error,
        evaluated=evaluated,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)