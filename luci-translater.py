import polib
import argparse
import os
import re
import openai
import tqdm
import datetime

def generate_po_file(input_file_path, output_file_path, target_language):
    input_text=""
    #if input file path is dir then get all files in dir
    if os.path.isdir(input_file_path):
        files=os.listdir(input_file_path)
        for file in files:
            if os.path.isdir(input_file_path +"/" + file):
                continue
            f = open(input_file_path +"/" + file, "r")
            iter_f = iter(f)
            for line in iter_f:
                input_text+=line
    else:         
        with open(input_file_path, 'r') as f:
            input_text = f.read()

    # Extract the text to be translated
    text_to_translate = re.findall(r'\_\((.*?)\)', input_text)
    for i, text in enumerate(text_to_translate):
        text = text.replace('"', '')
        text = text.replace("'", '')
    
    text_to_translate = list(set(text_to_translate))

        
    # Translate the text using OpenAI API
    translated_text = []
    for text in tqdm.tqdm(text_to_translate):
        #remove quotes
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Translate the following text into {target_language}: '{text}'",
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.7,
        )

        if response.choices[0].text:
            translated_text.append(response.choices[0].text.strip())
        else:
            translated_text.append(text)

    # Generate the PO file
    po = polib.POFile()


    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'jacky.chen@esix.co',
        'POT-Creation-Date': current_time,
        'PO-Revision-Date': current_time,
        'Last-Translator': 'Jacky Chan <jacky.chen@esix.co>',
        'Language-Team': str(target_language) + ' <jacky.chen@esix.co>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    
    po.metadata = metadata
    for i, text in enumerate(text_to_translate):
        #remove quotes
        text = text.replace('"', '')
        text = text.replace("'", '')
        entry = polib.POEntry(
            msgid=text,
            msgstr=translated_text[i],
        )
        po.append(entry)
    po.save(output_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate PO file from input file')
    parser.add_argument('input_file_path', required=True,type=str, help='Path to input file')
    parser.add_argument('output_file_path',required=False, type=str, help='Path to output PO file')
    parser.add_argument('target_language',required=False, type=str, help='Target language for translation')
    args = parser.parse_args()

    if not args.output_file_path:
        output_file_path = os.path.splitext(args.input_file_path)[0] + '.po'
    else:
        output_file_path = args.output_file_path

    if not args.target_language:
        target_language = 'Simplified Chinese'
    else:
        target_language = args.target_language

    # Check if OpenAI API key is available
    # OPENAI_API_KEY
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not found.")
        exit(1)
    
    generate_po_file(args.input_file_path, output_file_path,  target_language)
