import os
import re
import copy
import subprocess
import json
from pathlib import Path

__TAB__ = "  " # yml indents are set at 2 spaces
__GEN_DIR__= os.path.join(os.path.dirname(os.path.realpath(__file__)))

req_gens = []
req_gens.append(os.path.join(__GEN_DIR__, "pipreq.sh"))
req_gens.append(os.path.join(__GEN_DIR__, "nodereq.sh"))

def walklevel(some_dir, level=1):
  some_dir = some_dir.rstrip(os.path.sep)
  assert os.path.isdir(some_dir)
  num_sep = some_dir.count(os.path.sep)
  for root, dirs, files in os.walk(some_dir):
    yield root, dirs, files
    num_sep_this = root.count(os.path.sep)
    if num_sep + level <= num_sep_this:
      del dirs[:]


def tab_gen(num_tabs):
  tabs = ""
  for x in range(0,num_tabs):
    tabs += __TAB__
  return tabs


def generate_aws_framework(project, template_dir, service_name):
  functions = find_functions(project)
  sls_template = template_dir + "/serverless.yml"
  aws_provider_template = template_dir + "/aws-provider.yml"

  generate_sls_yml(project, sls_template, service_name, functions)
  generate_config_files(project, aws_provider_template, functions)
  generate_requirements(project)


def generate_sls_yml(project, template, service_name, functions):
  template_path = Path(template)
  if not template_path.is_file():
    raise ValueError("Template file not found.")

  if not Path(project).is_dir():
    raise ValueError("Project directory not found.")

  dest_path = os.path.join(project,"serverless.yml")

  if not Path(dest_path).is_file():
    bashCommand = "cp {} {}".format(template_path, dest_path)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is not None:
      raise Exception(error)

  with open(template_path, "r") as source:
    with open(dest_path, "w") as target:
      data = source.read()
      changed = data.replace('SERVICE_NAME',service_name)
      target.write(changed)

  append_function_defs(dest_path, functions)
  append_python_function_mappings(dest_path, functions)


def find_functions(project):
  generators = walklevel(project, 1)
  generators_sum = sum(1 for _ in enumerate(walklevel(project, 2)))-1
  
  count = 0
  functions = []
  for pos, gen in enumerate(generators):

    # skips root of project
    if count == 0:
      count += 1
      continue

    functions.append({
      'parent': gen[0].split("/")[-1],
      'name': gen[2][0].split("/")[-1].split(".")[0],
      'ext': gen[2][0].split("/")[-1].split(".")[1]
    })

  return functions


def append_function_defs(filepath, functions):
  with open(filepath, "a") as target:
    for f in functions:
      target.write("\n{}{}: ${{file({}/environments/${{self:custom.stage}}.json)}}".format(tab_gen(1), f['parent'], f['parent']))


def append_python_function_mappings(filepath, functions):
  append_string = "{}pythonRequirements:\n{}zip: true\n{}pyIndividually:".format(tab_gen(1),tab_gen(2),tab_gen(1))
  for f in functions:
    if f['ext'] == "py":
      append_string += "\n{}wrap:{}: {}/{}.lambda_handler".format(tab_gen(2),f['parent'],f['parent'],f['parent']+"_lmbd")
  append_string += "\n"

  with open(filepath, "r") as in_file:
    buf = in_file.readlines()

  with open(filepath, "w") as out_file:
    for line in buf:
      if "service:" in line:
        line = line + "\nplugins:\n{}- serverless-python-individually\n".format(tab_gen(1))
      if "custom:" in line:
        line = line + append_string
      out_file.write(line)  


def generate_config_files(project, template, functions):
  # generate provider config for overall project
  provider_config_dir = "/".join([project, "environments"])
  if not Path(provider_config_dir).is_dir():
    bashCommand = "mkdir {}".format(provider_config_dir)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is not None:
      raise Exception(error)
    
    bashCommand = "cp {} {}".format(template, provider_config_dir+"/example.yml")
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is not None:
      raise Exception(error)

  # generate function configs
  for f in functions:
    if f['ext'] == "py":
      handler = f['parent']+"/wrap.handler"
      runtime = "python3.6"
    elif f['ext'] == "js":
      handler = f['parent']+"/index.handler"
      runtime = "nodejs6.10"

    filepath = "/".join([project, f['parent'], "environments"])
    if not Path(filepath).is_dir():
      bashCommand = "mkdir {}".format(filepath)
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      if error is not None:
        raise Exception(error)

    config_path = "/".join([filepath,"example.json"])
    if not Path(config_path).is_file():
      config = {
        "name": f['parent'],
        "runtime": runtime,
        "memorySize": "256",
        "timeout": "30",
        "handler": handler,
        "package": {
          "include": ["{}/**".format(f['parent'])]
        }
      }

      with open(config_path, 'w') as outfile:
        json.dump(config, outfile, indent=4)


def generate_requirements(project):
  for req_gen in req_gens:
    process = subprocess.Popen(args=[str(req_gen), str(project), str(__GEN_DIR__)], stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is not None:
      raise Exception(error)