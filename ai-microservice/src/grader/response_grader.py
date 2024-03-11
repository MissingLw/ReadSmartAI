"""
Response_grader.py is a Python script that uses OpenAI to grade student responses to reading comprehension questions. The script reads the correct answers and student responses from two files, compares the responses, and generates feedback for each question. The feedback is then written to a file.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request
app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)

client = OpenAI(api_key=api_key)


def read_file(file_path):
    """
    Read a file and return its content as a dictionary.
    
    Args:
        file_path (str): The path of the file to read.

    Returns:
        dict: A dictionary where the keys are question numbers and the values are the corresponding answers.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    content_dict = {}
    for line in lines:
        if line.strip():  # ignore empty lines
            if line.startswith('Answer'): 
                number, content = line.split(': ', 1)
                content_dict[number] = content.strip()
    return content_dict


def compare_responses(qa_pairs, student_responses):
    """
    Compare student responses with correct answers and generate feedback.

    Args:
        qa_pairs (dict): A dictionary where the keys are question numbers and the values are the correct answers.
        student_responses (dict): A dictionary where the keys are question numbers and the values are the student's answers.

    Returns:
        list: A list of feedback strings for each question.
    """
    feedback = []
    # Replace 'Question ' with 'Answer ' in student_responses keys
    student_responses = {k.replace('Question ', 'Answer '): v for k, v in student_responses.items()}
    print(f"qa_pairs: {qa_pairs}")
    print(f"student response is;  {student_responses}\n")
    print(f"qa_pairs keys: {qa_pairs.keys()}")
    print(f"student_responses keys: {student_responses.keys()}")
    for number, correct_answer in qa_pairs.items():
        student_answer = student_responses.get(number, '')
        print(f"student answer is;  {student_answer}\n")
        prompt = f"Correct answer is: {correct_answer}. Student's answer is: {student_answer}. Is the student's answer correct? Please format the start of your response as follows: Correct/Incorrect: Feedback"
        ai_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant evaluating student responses. Determine if responses are generally correct based on key points. Provide detailed feedback for incorrect answers identifying key points missed."},
                # {"role": "system", "content": "You are a helpful assistant that evaluates student responses to reading comprehension questions. You are trying to see if a student is generally correct or incorrect in their response, a correct response is one where they had got most of the key points and ideas correct. Provide detailed feedback for incorrect answers and identify the key points that the student missed."},
                {"role": "user", "content": prompt},
            ]
        )
        ai_feedback = ai_response.choices[0].message.content.strip()
        if ai_feedback.startswith("Correct:"):
            ai_append = ai_feedback.split(':', 1)[1].strip()
            #  feedback.append(f"Correct: {correct_answer}\n{ai_append}")
            feedback.append(f"Correct: {ai_append}\n Expected Answer: {correct_answer}")
            #  feedback.append(f"Correct: {ai_append}")
        elif ai_feedback.startswith("Incorrect:"):
            ai_append = ai_feedback.split(':', 1)[1].strip()
            #  feedback.append(f"Incorrect: {ai_append}")
            feedback.append(f"Incorrect: {ai_append}\n Expected Answer: {correct_answer}")
    return feedback


def write_feedback_to_file(feedback, file_path):
    """
    Write feedback to a file.

    Args:
        feedback (list): A list of feedback strings.
        file_path (str): The path of the file to write to.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        for i, response in enumerate(feedback):
            file.write(f"Feedback {i+1}: {response}\n\n")


def main():
    """
    Main function to read files, compare responses, and write feedback.
    """
    qa_pairs = read_file('qa_pairs.txt')
    student_responses = read_file('student_responses.txt')
    # for i in qa_pairs.items(): print(i) # Debug
    # for i in student_responses.items(): print(i) # Debug
    feedback = compare_responses(qa_pairs, student_responses)
    write_feedback_to_file(feedback, 'feedback.txt')


@app.route('/grade', methods=['POST'])
def grade():
    data = request.get_json()
    qa_pairs = data['qa_pairs']
    student_responses = data['student_responses']
    qa_pairs = {f'Answer {i+1}': answer for i, (_, answer) in enumerate(qa_pairs['qa_pairs'])}
    print(student_responses)
    feedback = compare_responses(qa_pairs, student_responses)
    return {'feedback': feedback}


if __name__ == "__main__":
    app.run(port=5001)
