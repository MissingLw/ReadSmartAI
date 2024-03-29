"""
Question_generator.py creates a list of reading comprehension question/answer pairs for a given text file
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request
app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)

client = OpenAI(api_key=api_key)


def read_text_from_file(file_path):
    """
    Reads a text file and returns its content as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as scode:
        text = scode.read().replace('\n', '')
    return text


def generate_qa_pairs(text, num_questions):
    """
    Generates reading comprehension questions and answers for a given text.
    """
    prompt = f"{text}\n\nGenerate {num_questions} reading comprehension questions and their answers focusing on core ideas/themes. Please format them as follows:\nQuestion Number: Question\nAnswer: Answer\n\nFor example:\nQuestion 1: What is the color of the sky?\nAnswer: The sky is blue.\n\n"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    qa_pairs = []
    for choice in response.choices:
        message = choice.message
        print(f"Processing message with role {message.role} and content\n {message.content}")  # Debug
        if message.role == 'system':
            continue
        elif message.role == 'assistant':
            qa = message.content.split('\n')  # Split the message into separate lines
            for i, line in enumerate(qa):  # Iterate over every line
                if line.startswith('Question'):  # Check if the line is a question
                    print("question recognized")  # debug
                    question = line.split(': ', 1)[1]  # Split on ': ' and take the second part as the question
                elif line.startswith('Answer:'):  # Check if the line is an answer
                    answer = line.split('Answer:', 1)[1]  # Split on 'Answer:' and take the second part as the answer
                    qa_pairs.append((question.strip(), answer.strip()))  # Append the question and answer, removing any leading/trailing whitespace
                    print(f"TEST PAIR;  {qa_pairs}\n")
    print(f"\n\n\n\n\nTHIS IS QA PAIRS;  {qa_pairs}\n")
    return qa_pairs, response


def write_qa_pairs_to_file(responses, file_path):
    """
    Writes a list of reading comprehension question/answer pairs to a file.
    """
    print(f"Writing QA pairs to file: {file_path}")  # Debug: print the file path
    with open(file_path, 'w', encoding='utf-8') as file:
        print("File Sucessfully Opened")  # Debug: print a message when the file is opened
        print(f"Number of QA pairs: {len(responses)}")  # Debug: print the number of QA pairs
        for i, (question, answer) in enumerate(responses):
            print(f"Writing QA pair {i+1}")  # Debug: print the index of the QA pair
            file.write(f"Question {i+1}: {question}\n")
            file.write(f"Answer {i+1}: {answer}\n\n")
    print("Finished writing QA pairs")  # Debug: print a message when done


def main():
    """
    Main function to read files, compare responses, and write feedback.
    """
    text = read_text_from_file('tell_tale_heart.txt')
    responses, full_response = generate_qa_pairs(text, 5)
    # print(full_response)
    write_qa_pairs_to_file(responses, 'qa_pairs.txt')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    textSource = data['textSource']
    numQuestions = data['numQuestions']

    # Read the text from the file specified by textSource
    text = read_text_from_file(f'{textSource}.txt')

    # Generate the specified number of questions
    qa_pairs, _ = generate_qa_pairs(text, numQuestions)

    return {'qa_pairs': qa_pairs}


if __name__ == "__main__":
    app.run(port=5000)