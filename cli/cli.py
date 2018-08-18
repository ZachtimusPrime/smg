import click
import os
from generator import generator

__template_dir__= os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

@click.group()
def main():
    """
    Simple CLI for migrating pre-existing lambda files to use the serverless framework.
    """
    pass

@main.command()
@click.option('--path', '-p', default=os.getcwd(), help="The filepath to the directory of lambdas to migrate.")
def migrate2aws(path):
    """Creates file structure necessary to deploy lambdas with serverless."""
    project_name = path.split("/")[-1]

    try:
      generator.generate_aws_framework(path, __template_dir__, project_name)
    except Exception as e:
      click.echo(e)