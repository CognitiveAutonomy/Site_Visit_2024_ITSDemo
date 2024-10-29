import sys
import openai
from openai import OpenAI
# openai.api_key = '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'
client = OpenAI(
    api_key='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',
)

def chat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def main(argv):
    prompt = input("You: ")
    response = chat_gpt(prompt)

    print(response)

if __name__ == '__main__':
    main(sys.argv[1:])
