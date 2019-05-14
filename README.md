# CSE P 590 Mutation Report HTML Generator

## Usage

`generate_html.py` uses `argparse` so you can just run `python generate_html.py --help` to see the required
arguments which are as follows:

- `input_directory`, the input directory containing the `.json` files to generate the HTML report out of
    - In the top level of the directory there must be `index.json` and `input_paths.json` files accompanied
    by a `mutants/` folder containing `.json` files for each of the mutants
- `output_directory`, the directory to write the generated `.html` files to
    - Will have a similar structure to the input directory, top level `index.html` and `original_code.html` files 
    accompanied by a `mutants` folder containing a `.html` file for each of the generated mutants

The input `.json` files must have a specific input format, see [below](#json-structure)

## Examples

Inside of the top level `examples` directory there are two files, `my_class.py` and `my_class_test.py` to generate
example `.json` files we can use the modified version of `mutpy` included in the top level directory.

### Install Modified Version of MutPy

I'd recommend creating a activating new anaconda environment with a version of 3.7 with:
```
conda create -n test_env python=3.7
conda activate test_env
```
and then navigating to the `mutpy` folder contained in this repository and running:
```
pip install -e .
```
Which will install the modified `mutpy` for this conda environment.

To generate the example `.json` files run:
```
mut.py --target my_class --unit-test my_class_test --report-html output
```
This will take the module `my_class.py` from the current directory and mutate it and then run
the tests in the test suite `my_class_test.py` and generate the `.json` output files to the `output/` folder

To create the example HTML files we then navigate back up to the top-level directory and run:
```
python generate_html.py example/output/ html_output/
```
which will take the `.json` files in `example/output/` that you generated with the previous command and 
construct the `.html` files and place them into `html_output/`

## TODO

- [ ] Add an overall view of the original Python program in `index.html` where all of the mutated sections
are highlighted
    - Potentially make the lines clickable to see a view of the possible mutants that can be generated?
    - Or maybe some tooltip annotations saying what operator is being modified and how by which Mutation operator?
- [ ] In each individual mutant report somehow indicate what the un-mutated code was so that the user can compare
the mutation to the original and conceive of how to write a test to kill that mutant or decide if it is equivalent
- [ ] Add an option to mark a mutant as equivalent and then somehow store that information
- [ ] Include a `tests.html` page that gives a list of the tests and the mutants that they killed? Could potentially
be useful for viewing which tests are effective

## JSON Structure

### Index Object Format

```
{
    "targets" : [<string>, ...],        // the tested modules
    "tests" : [                         // the tests run on the module
        ["test_name", "test_target", "test_execution_time"],
        ...
    ],
    "number_of_tests" : <int>,          // number of tests ran
    "score" : {                         // from the mutpy MutationScore object
        "count" : <float>,              // the calculated mutation score
        "covered_nodes" : <int>,        // 
        "all_nodes" : <int>,            // 
        "killed_mutants" : <int>,       // number of killed mutants
        "timeout_mutants" : <int>,      // mutants that timed out
        "incompetent_mutants" : <int>,  // unclear...
        "survived_mutants" : <int>,     // number of living mutants
        "all_mutants" : <int>           // total number of mutants
    },
    "duration" : <float>,               // duration of the testing process
    "date_now" : <string>               // the date/time that the mutants were generated/tested
}
```

### Input Paths Object Format

TODO

### Mutant Object Format

```
{
    "mutant_code" : <string>,           // entire mutation source code
    "number" : <int>,                   // the mutation number
    "mutations" : [                     // list of applied mutations (mostly just 1, could be more
        {                                   // for higher order mutations)
            "operator" : <string>,      // the mutation operator applied
            "lineno" : <int>            // the changed line number
        },
        ...
    ],
    "module" : <string>,                // the mutated module
    "status" : <string>,                // killed, incompetent, survived
    "time" :  <float>,                  // time it took tests to run
    "killer" : <string>,                // the test and test suite that killed the mutant
    "tests_run" : <int>,                // number of tests run to kill
    "exception_traceback" : <string>    // generated exception traceback when killed
}
```