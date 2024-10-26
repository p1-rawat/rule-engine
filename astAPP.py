from flask import Flask, request, jsonify, render_template
import re
from database import create_connection, insert_rule

app = Flask(__name__)
connection = create_connection()

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def parse_rule(rule):
    tokens = re.findall(r'\w+|==|!=|<=|>=|<|>', rule)

    def build_tree(tokens):
        if len(tokens) == 1:
            return Node(tokens[0])
        elif len(tokens) >= 3:
            left = Node(tokens[0] + ' ' + tokens[1] + ' ' + tokens[2]) 
            if len(tokens) > 3:
                right = build_tree(tokens[3:])
                return Node("OR", left, right)
            return left
        return None

    return build_tree(tokens)

def tree_to_dict(node):
    if node is None:
        return None
    return {
        "value": node.value,
        "left": tree_to_dict(node.left),
        "right": tree_to_dict(node.right)
    }

def evaluate_rule(node, user_data):
    if node is None:
        return False
    
    # Leaf node - checking conditions
    if node.left is None and node.right is None:
        # Check if the node.value has a space (indicating it has a field and a value)
        if ' ' in node.value:
            parts = node.value.split(' ')
            if len(parts) == 3: 
                field, operator, value = parts
                user_value = user_data.get(field)

                if user_value is not None:
                    if operator == '==':
                        return user_value == int(value)  # Assuming integers for comparison
                    elif operator == '!=':
                        return user_value != int(value)
                    elif operator == '>':
                        return user_value > int(value)
                    elif operator == '<':
                        return user_value < int(value)
                    elif operator == '>=':
                        return user_value >= int(value)
                    elif operator == '<=':
                        return user_value <= int(value)
        else:
            print(f"Unexpected leaf node value: {node.value}")
            return False

    left_eval = evaluate_rule(node.left, user_data)
    right_eval = evaluate_rule(node.right, user_data)

    if node.value in ["AND", "OR"]:
        if node.value == "OR":
            return left_eval or right_eval
        elif node.value == "AND":
            return left_eval and right_eval
    else:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.get_json()
    rule = data['rule']
    
    ast_root = parse_rule(rule)
    ast_dict = tree_to_dict(ast_root)

    # Insert the rule into the database
    insert_rule(connection, rule)

    return jsonify(ast=ast_dict)

@app.route('/check_eligibility', methods=['POST'])
def check_eligibility():
    user_data = request.get_json()

    rules = ["age > 30", "department == 'Engineering'"]  # Placeholder for actual rules

    eligibility = False

    for rule in rules:
        ast_root = parse_rule(rule)
        if evaluate_rule(ast_root, user_data):
            eligibility = True
            break

    return jsonify(message="Eligible" if eligibility else "Not Eligible")

if __name__ == '__main__':
    app.run(debug=True)
