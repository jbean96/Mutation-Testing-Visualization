import argparse
import glob
import jinja2
import json
import os
import re
from typing import Any, Dict, List

MUTANT_FOLDER="mutants"
TEMPLATE_FOLDER="templates"

class HTMLGenerator():
    def __init__(self, paths : Dict):
        self._index_path = paths["index_path"]
        self._input_paths_path = paths["input_paths_path"]
        self._mutants_folder = paths["mutants_folder"]
        self._output_folder = paths["output_folder"]
        self._jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=paths["templates_folder"]))
        self._mutations : List = None

    def generate_original_code_html(self, module : str):
        """Generate the html page for the original code of the mutated module
        with highlights on the lines that had mutations
        """
        try:
            with open(self._input_paths_path, 'r') as data_file:
                input_paths_obj = json.load(data_file)
            data_file.closed
        except:
            raise Exception("Error parsing %s" % self._input_paths_path)

        if module not in input_paths_obj:
            raise Exception("No input path in %s for module %s" % (self._input_paths_path, module))
        
        try:
            with open(input_paths_obj[module], 'r') as data_file:
                original_code = data_file.read()
            data_file.closed
        except:
            raise Exception("Error reading module %s from %s" % (module, input_paths_obj[module]))

        # filter out the mutations not relevant to this module
        mutations = list(filter(lambda x: x["module"] == module, self._mutations))

        original_code_template = self._jinja_env.get_template("original_code.html")

        ##### TODO: Mutations not properly being highlighted in the original_code.html file #####
        context = {
            "original_code" : original_code,
            "mutations" : mutations
        }
        report = original_code_template.render(context)
        self._write_report_to_output_folder("original_code.html", report)

    def _write_report_to_output_folder(self, file_name : str, report : str):
        """Writes the report to the correct output file"""
        if file_name[file_name.rfind('.'):] != ".html":
            raise Exception("Output file must have extension .html, files is named %s" % file_name)

        output_path = os.path.join(self._output_folder, file_name)
        with open(output_path, 'w') as output_file:
            output_file.write(report)
        output_file.closed

    def _get_targets(self) -> List[str]:
        """Returns a list of modules modified"""
        try:
            with open(self._index_path, 'r') as data_file:
                index_obj = json.load(data_file)
            data_file.closed
            return index_obj["targets"]
        except:
            raise Exception("Error parsing %s" % self._index_path)

    def generate_index_html(self):
        """Generate the index page for the html report. Note that mutation
        info is empty until you call set_mutations() on this HTMLGenerator
        object
        """
        try:
            with open(self._index_path, 'r') as data_file:
                index_obj = json.load(data_file)
            data_file.closed
        except:
            raise Exception("Error parsing %s" % self._index_path)

        index_template = self._jinja_env.get_template("index.html")
        context = {
            "targets" : index_obj["targets"],
            "tests" : index_obj["tests"],
            "number_of_tests" : index_obj["number_of_tests"],
            "score" : index_obj["score"],
            "duration" : index_obj["duration"],
            "mutations" : self._mutations if self._mutations is not None else [],
            "date_now" : index_obj["date_now"]
        }
        report = index_template.render(context)
        self._write_report_to_output_folder("index.html", report)
        # output_path = os.path.join(self._output_folder, "index.html")
        # with open(output_path, 'w') as output_file:
        #     output_file.write(report)
        # output_file.closed

    def set_mutations(self, mutations : List[Any] = None):
        """Sets the mutations field for this HTMLGenerator object to be used
        in the original code and index html generation
        """
        if mutations is not None:
            self._mutations = mutations
        else:
            self._mutations = self.get_mutation_info_for_index()

    def get_mutation_info_for_index(self) -> List:
        """Iterates through the mutant .json files and pulls the information
        needed as a summary for the index html page and for annotations in the
        original code html page, returns a list of these objects containing
        the information for each mutation
        """
        mutations = []
        for f in self.get_mutant_files():
            try:
                with open(f, 'r') as data_file:
                    mutant_obj = json.load(data_file)
                data_file.closed
            except:
                raise Exception("Error parsing %s" % f)

            mutations.append({
                "number" : mutant_obj["number"],
                "mutations" : mutant_obj["mutations"],
                "module" : mutant_obj["module"],
                "status" : mutant_obj["status"],
                "time" : mutant_obj["time"],
                "killer" : mutant_obj["killer"],
                "tests_run" : mutant_obj["tests_run"]
            })
        return mutations

    def get_mutant_files(self):
        """Iterates over the mutant .json files in the mutant folder"""
        file_names = glob.glob(os.path.join(self._mutants_folder, "*.json"))
        for f in file_names:
            yield f

    def generate_mutant_html(self, mutant_file : str):
        """Generates the mutant html file for the specified .json file"""
        try:
            with open(mutant_file, 'r') as data_file:
                mutant_obj = json.load(data_file)
            data_file.closed
        except:
            raise Exception("Error parsing %s" % mutant_file)

        detail_template = self._jinja_env.get_template("detail.html")

        report = detail_template.render(mutant_obj)
        self._write_report_to_output_folder("%d.html" % mutant_obj["number"], report)
        # output_path = os.path.join(self._output_folder, MUTANT_FOLDER, "%d.html" % mutant_obj["number"])
        # with open(output_path, 'w') as output_file:
        #     output_file.write(report)
        # output_file.closed

    def generate_all(self):
        self.set_mutations()
        self.generate_index_html()
        ##### TODO: Fix original_code.html generation and get mutpy to produce an input_paths.json file #####
        # for target in self._get_targets():
        #     self.generate_original_code_html(target)

        for mutant_file in self.get_mutant_files():
            self.generate_mutant_html(mutant_file)

def main(paths : Dict):
    html_gen = HTMLGenerator(paths)
    html_gen.generate_all()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a HTML mutation testing portal")
    parser.add_argument("input_directory", type=str, help="The directory containing the JSON files")
    parser.add_argument("output_directory", type=str, help="The output directory to placd generated html files")

    args = parser.parse_args()

    if not os.path.isdir(args.input_directory):
        raise Exception("Directory \"%s\" does not exist" % args.input_directory)
    
    index_path = os.path.join(args.input_directory, "index.json")
    if not os.path.isfile(index_path):
        raise Exception("File \"index.json\" is missing from %s" % args.input_directory)

    input_paths_path = os.path.join(args.input_directory, "input_paths.json")
    if not os.path.isfile(input_paths_path):
        raise Exception("File \"input_paths.json\" is missing from %s" % args.input_directory)

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
        "input_paths_path" : os.path.normpath(input_paths_path),
        "mutants_folder" : os.path.normpath(mutants_folder),
        "templates_folder" : os.path.normpath(templates_folder),
        "output_folder" : os.path.normpath(output_folder)
    }
    
    main(files)