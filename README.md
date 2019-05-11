# CSE P 590 Mutation Report HTML Generator

## Usage

`generate_html.py` uses `argparse` so you can just run `python generate_html.py --help` to see the required
arguments which are as follows:

- `input_directory`, the input directory containing the `.json` files to generate the HTML report out of
    - In the top level of the directory there must be an `index.json` file accompanied by a `mutants/` folder
    containing `.json` files for each of the mutants
        - This may change soon given that `index.json` contains all of the mutant objects already
- `output_directory`, the directory to write the generated `.html` files to
    - Will have the same structure as the input directory, a top level `index.html` file accompanies by a
    `mutants` folder containing a `.html` file for each of the generated mutants

The input `.json` files must have a specific input format, see [below](#JSON_Structure)

## Examples

Inside of the top level `examples` directory there are two files, `my_class.py` and `my_class_test.py` and then
an associated folder `output` that contains the corresponding `.json` output that needs to be generated for
the program to generate the HTML report.

## TODO

- [] Add an overall view of the original Python program in `index.html` where all of the mutated sections
are highlighted
    - Potentially make the lines clickable to see a view of the possible mutants that can be generated?
    - Or maybe some tooltip annotations saying what operator is being modified and how by which Mutation operator?
- [] In each individual mutant report somehow indicate what the un-mutated code was so that the user can compare
the mutation to the original and conceive of how to write a test to kill that mutant or decide if it is equivalent
- [] Add an option to mark a mutant as equivalent and then somehow store that information
- [] Include a `tests.html` page that gives a list of the tests and the mutants that they killed? Could potentially
be useful for viewing which tests are effective

## JSON Structure

### Index Object Format

```json
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
    "mutations" : [                     // list of all generated mutants
        <mutation object format>,       // see below
        ...
    ],
    "date_now" : <string>               // the date/time that the mutants were generated/tested
}
```

### Mutant Object Format

```json
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