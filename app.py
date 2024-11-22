from flask import Flask, request, jsonify, render_template
import pandas as pd
import pdfplumber
import openai

app = Flask(__name__)

excel_path = 'Database_Error_codes_Tickets.csv'
df = pd.read_csv(excel_path)

def find_solution_in_excel(issue):
    solutions = []
    for index, row in df.iterrows():
        if issue.lower() in row['Description'].lower():  # Check if issue matches
            # Append the solution to the list with a step number
            solutions.append(f"Step {len(solutions) + 1}: {row['Resolution Steps']}")
    return solutions if solutions else None


pdf_path = 'e12152-User Guide.pdf'

def search_pdf(issue):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if issue.lower() in text.lower():
                return text.strip()
    return None

openai.api_type = "azure"
openai.api_base = "https://react-ticketing-openai.openai.azure.com/"
openai.api_version = "2024-08-01-preview"
openai.api_key = "6r0HQtbI6bksgMkxcdD7R3bSGIqDASz5qDCSI7hpTE4EX1XWBV1hJQQJ99AKACYeBjFXJ3w3AAABACOGMi7L"

def gpt_4_solution(issue):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert assistant helping resolve issues.For each solution, provide a detailed step by step explanation of how it helps resolve the error in solution 3(GPT)."},
            {"role": "user", "content": f"The issue is: {issue}"}
        ],
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/get_solutions/', methods=['POST'])
def get_solutions():
    issue = request.form.get('issue')  

    if not issue:
        return jsonify({"error": "Issue is required."}), 400

    excel_solution = find_solution_in_excel(issue)
    pdf_solution = search_pdf(issue)
    gpt_solution = gpt_4_solution(issue)

    solutions = {
        "Solution 1 (Excel)": excel_solution if excel_solution else "No solution found in Excel.",
        "Solution 2 (PDF)": pdf_solution if pdf_solution else "No solution found in Product Manuel.",
        "Solution 3 (GPT-4)": gpt_solution
    }

    return render_template('index.html', issue=issue, solutions=solutions)

if __name__ == '__main__':
    app.run(debug=True)