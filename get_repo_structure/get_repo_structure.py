import argparse
import ast
import json
import os
import subprocess
import time
import uuid

import pandas as pd
from tqdm import tqdm

repo_to_top_folder = {
    "django/django": "django",
    "sphinx-doc/sphinx": "sphinx",
    "scikit-learn/scikit-learn": "scikit-learn",
    "sympy/sympy": "sympy",
    "pytest-dev/pytest": "pytest",
    "matplotlib/matplotlib": "matplotlib",
    "astropy/astropy": "astropy",
    "pydata/xarray": "xarray",
    "mwaskom/seaborn": "seaborn",
    "psf/requests": "requests",
    "pylint-dev/pylint": "pylint",
    "pallets/flask": "flask",
}


def checkout_commit(repo_path, commit_id):
    """Checkout the specified commit in the given local git repository with retry.
    :param repo_path: Path to the local git repository
    :param commit_id: Commit ID to checkout
    :return: None
    """
    max_retries = 3
    retry_delay = 3  # seconds

    for attempt in range(max_retries):
        try:
            print(f"Checking out commit {commit_id} in repository at {repo_path}...")
            subprocess.run(
                ["git", "-C", repo_path, "checkout", commit_id],
                check=True,
                timeout=60,
                capture_output=True
            )
            print("Commit checked out successfully.")
            return  # Success

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running git command: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(retry_delay)
            else:
                raise RuntimeError(f"Failed to checkout {commit_id} after {max_retries} attempts: {e}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise


def clone_repo(repo_name, repo_playground):
    """Clone repository with retry mechanism for network errors"""
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            print(
                f"Cloning repository from https://github.com/{repo_name}.git to {repo_playground}/{repo_to_top_folder[repo_name]}..."
            )
            if attempt > 0:
                print(f"  (Attempt {attempt + 1}/{max_retries})")

            # Add timeout and better error handling
            # Note: Not using --depth=1 because we need to checkout specific commits
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    f"https://github.com/{repo_name}.git",
                    f"{repo_playground}/{repo_to_top_folder[repo_name]}",
                ],
                check=True,
                timeout=600,  # 10 minute timeout for full clone
                capture_output=True,
                text=True
            )
            print("Repository cloned successfully.")
            return  # Success, exit function

        except subprocess.TimeoutExpired:
            print(f"Clone timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Clean up partial clone
                subprocess.run(
                    ["rm", "-rf", f"{repo_playground}/{repo_to_top_folder[repo_name]}"],
                    check=False
                )
            else:
                raise RuntimeError(f"Failed to clone {repo_name} after {max_retries} attempts (timeout)")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running git command: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")

            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Clean up partial clone
                subprocess.run(
                    ["rm", "-rf", f"{repo_playground}/{repo_to_top_folder[repo_name]}"],
                    check=False
                )
            else:
                raise RuntimeError(f"Failed to clone {repo_name} after {max_retries} attempts: {e}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Clean up partial clone
                subprocess.run(
                    ["rm", "-rf", f"{repo_playground}/{repo_to_top_folder[repo_name]}"],
                    check=False
                )
            else:
                raise


def get_project_structure_from_scratch(
    repo_name, commit_id, instance_id, repo_playground
):

    # Generate a temperary folder and add uuid to avoid collision
    repo_playground = os.path.join(repo_playground, str(uuid.uuid4()))

    # assert playground doesn't exist
    assert not os.path.exists(repo_playground), f"{repo_playground} already exists"

    # create playground
    os.makedirs(repo_playground)

    clone_repo(repo_name, repo_playground)
    checkout_commit(f"{repo_playground}/{repo_to_top_folder[repo_name]}", commit_id)
    structure = create_structure(f"{repo_playground}/{repo_to_top_folder[repo_name]}")
    # clean up
    subprocess.run(
        ["rm", "-rf", f"{repo_playground}/{repo_to_top_folder[repo_name]}"], check=True
    )
    d = {
        "repo": repo_name,
        "base_commit": commit_id,
        "structure": structure,
        "instance_id": instance_id,
    }
    return d


def parse_python_file(file_path, file_content=None):
    """Parse a Python file to extract class and function definitions with their line numbers.
    :param file_path: Path to the Python file.
    :return: Class names, function names, and file contents
    """
    if file_content is None:
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                parsed_data = ast.parse(file_content)
        except Exception as e:  # Catch all types of exceptions
            print(f"Error in file {file_path}: {e}")
            return [], [], ""
    else:
        try:
            parsed_data = ast.parse(file_content)
        except Exception as e:  # Catch all types of exceptions
            print(f"Error in file {file_path}: {e}")
            return [], [], ""

    class_info = []
    function_names = []
    class_methods = set()

    for node in ast.walk(parsed_data):
        if isinstance(node, ast.ClassDef):
            methods = []
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    methods.append(
                        {
                            "name": n.name,
                            "start_line": n.lineno,
                            "end_line": n.end_lineno,
                            "text": file_content.splitlines()[
                                n.lineno - 1 : n.end_lineno
                            ],
                        }
                    )
                    class_methods.add(n.name)
            class_info.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "text": file_content.splitlines()[
                        node.lineno - 1 : node.end_lineno
                    ],
                    "methods": methods,
                }
            )
        elif isinstance(node, ast.FunctionDef) and not isinstance(
            node, ast.AsyncFunctionDef
        ):
            if node.name not in class_methods:
                function_names.append(
                    {
                        "name": node.name,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "text": file_content.splitlines()[
                            node.lineno - 1 : node.end_lineno
                        ],
                    }
                )

    return class_info, function_names, file_content.splitlines()


def create_structure(directory_path):
    """Create the structure of the repository directory by parsing Python files.
    :param directory_path: Path to the repository directory.
    :return: A dictionary representing the structure.
    """
    structure = {}

    for root, _, files in os.walk(directory_path):
        repo_name = os.path.basename(directory_path)
        relative_root = os.path.relpath(root, directory_path)
        if relative_root == ".":
            relative_root = repo_name
        curr_struct = structure
        for part in relative_root.split(os.sep):
            if part not in curr_struct:
                curr_struct[part] = {}
            curr_struct = curr_struct[part]
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                class_info, function_names, file_lines = parse_python_file(file_path)
                curr_struct[file_name] = {
                    "classes": class_info,
                    "functions": function_names,
                    "text": file_lines,
                }
            else:
                curr_struct[file_name] = {}

    return structure
