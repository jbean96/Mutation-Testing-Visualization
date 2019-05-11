import argparse
import glob
import jinja2
import json
import os
import re
from typing import Dict

MUTANT_FOLDER="mutants"
TEMPLATE_FOLDER="templates"

class HTMLGenerator():
    def __init__(self, paths : Dict):
        self.index_path = paths["index_path"]
        self.mutants_folder = paths["mutants_folder"]
        self.output_folder = paths["output_folder"]
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=paths["templates_folder"]))

    def generate_index_html(self):
        try:
            with open(self.index_path, 'r') as data_file:
                index_obj = json.load(data_file)
            data_file.closed
        except:
            raise Exception("Error parsing %s" % self.index_path)

        index_template = self.jinja_env.get_template("index.html")
        context = {
            "targets" : index_obj["targets"],
            "tests" : index_obj["tests"],
            "number_of_tests" : index_obj["number_of_tests"],
            "score" : index_obj["score"],
            "duration" : index_obj["duration"],
            "mutations" : index_obj["mutations"],
            "date_now" : index_obj["date_now"]
        }
        report = index_template.render(context)
        output_path = os.path.join(self.output_folder, "index.html")
        with open(output_path, 'w') as output_file:
            output_file.write(report)
        output_file.closed

    def get_mutant_files(self):
        file_names = glob.glob(os.path.join(self.mutants_folder, "*.json"))
        for f in file_names:
            yield f

    def generate_mutant_html(self, mutant_file : str):
        try:
            with open(mutant_file, 'r') as data_file:
                mutant_obj = json.load(data_file)
            data_file.closed
        except:
            raise Exception("Error parsing %s" % mutant_file)

        detail_template = self.jinja_env.get_template("detail.html")

        report = detail_template.render(mutant_obj)
        output_path = os.path.join(self.output_folder, MUTANT_FOLDER, "%d.html" % mutant_obj["number"])
        with open(output_path, 'w') as output_file:
            output_file.write(report)
        output_file.closed

def main(paths : Dict):
    html_gen = HTMLGenerator(paths)
    html_gen.generate_index_html()

    for mutant_file in html_gen.get_mutant_files():
        html_gen.generate_mutant_html(mutant_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a HTML mutation testing portal")
    parser.add_argument("input_directory", type=str, help="The directory containing the JSON files")
    parser.add_argument("output_directory", type=str, help="The output directory to placd generated html files")

    args = parser.parse_args()

    if not os.path.isdir(args.input_directory):
        raise Exception("Directory \"%s\" does not exist" % args.input_directory)
    
    index_path = os.path.join(args.input_directory, "index.json")
    if not os.path.isfile(index_path):
        raise Exception("File \"index.json\" missing in %s" % args.input_directory)

    mutants_folder = os.path.join(args.input_directory, MUTANT_FOLDER)
    if not os.path.isdir(mutants_folder):
        raise Exception("Folder \"%s\" not found in %s" % (MUTANT_FOLDER, args.input_directory))

    # os.path.dirname(__file__) gets the relative path to the directory of this file
    # this means that "templates" has to be in the same directory as this file for this
    # to function properly
    templates_folder = os.path.join(os.path.dirname(__file__), TEMPLATE_FOLDER)

    output_folder = args.output_directory
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, MUTANT_FOLDER), exist_ok=True)

    files = {
        "index_path" : os.path.normpath(index_path),
        "mutants_folder" : os.path.normpath(mutants_folder),
        "templates_folder" : os.path.normpath(templates_folder),
        "output_folder" : os.path.normpath(output_folder)
    }
    
    main(files)