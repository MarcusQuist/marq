# ========================================================================
# CHURN & LINES OF CODE
# ========================================================================

# ========================================================================
# Let's declare a var for the path where we're going to download a repository
# Warning: this must end in /
CODE_ROOT_FOLDER = "api/"

# ========================================================================
def top_level_package(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[:depth])

# ========================================================================
# extracting a module name from a rel path
def module_name_from_rel_path(full_path):

    # e.g. ../core/model/user.py -> zeeguu.core.model.user
    
    file_name = full_path.replace("/__init__.py","")
    file_name = file_name.replace("/",".")
    file_name = file_name.replace("\\", ".")
    file_name = file_name.replace(".py","")

    # remove the "api." prefix from package names
    if file_name.startswith("api."):
        file_name = file_name[4:]

    return file_name

assert ("tools.migrations.teacher_dashboard_migration_1.upgrade" == module_name_from_rel_path("tools/migrations/teacher_dashboard_migration_1/upgrade.py"))

assert ("zeeguu.api") == module_name_from_rel_path("zeeguu/api/__init__.py")


# ========================================================================
# CHURN
# ========================================================================

# ========================================================================
# get all commits in repository
from pydriller import Repository

def get_all_commits():
    return list(Repository(CODE_ROOT_FOLDER).traverse_commits())


# ========================================================================
# Count commits per file
from pydriller import ModificationType

def get_commits_per_file(all_commits):
    commit_counts = {}

    for commit in all_commits:
        for modification in commit.modified_files:
            
            new_path = modification.new_path
            old_path = modification.old_path
            
            try:

                if modification.change_type == ModificationType.RENAME:
                    commit_counts[new_path]=commit_counts.get(old_path,0)+1
                    commit_counts.pop(old_path)

                elif modification.change_type == ModificationType.DELETE:
                    commit_counts.pop(old_path, '')

                elif modification.change_type == ModificationType.ADD:
                    commit_counts[new_path] = 1

                else: # modification to existing file
                        commit_counts [old_path] += 1
            except Exception as e: 
                print("something went wrong with: " + str(modification))
                pass
            
    return commit_counts


# ========================================================================
# Count commits per package based on DEPTH
from collections import defaultdict

def get_commit_activity(depth=1):
    package_activity = defaultdict(int)

    commit_counts = get_commits_per_file(get_all_commits())

    for path, count in commit_counts.items():
        if ".py" in str(path):
            l2_module = top_level_package(module_name_from_rel_path(path), depth)
            package_activity[l2_module] += count

    sorted(package_activity.items(), key=lambda x: x[1], reverse=True)
    return package_activity
# ========================================================================

import os

# ========================================================================
# get the number of lines of code in a file
def count_lines_of_code(filepath):
    with open(filepath, 'r') as f:
        return sum(1 for line in f if line.strip() and not line.startswith('#'))

# ========================================================================
# get all files in a directory (recursively)
def get_all_files_in_directory(dirpath):
    for root, _, files in os.walk(dirpath):
        for file in files:
            yield os.path.join(root, file)

# ========================================================================
# count lines of code per file
def get_lines_of_code_per_file():
    lines_of_code = {}

    for filepath in get_all_files_in_directory(CODE_ROOT_FOLDER):
        if filepath.endswith('.py'):
            lines_of_code[filepath] = count_lines_of_code(filepath)

    return lines_of_code

# ========================================================================
# count lines of code per package based on DEPTH
from collections import defaultdict

def get_lines_of_code_activity(depth=1):
    package_activity = defaultdict(int)

    lines_of_code = get_lines_of_code_per_file()

    for filepath, count in lines_of_code.items():
        l2_module = top_level_package(module_name_from_rel_path(filepath), depth)
        package_activity[l2_module] += count

    # print(sorted(package_activity.items(), key=lambda x: x[1], reverse=True))
    return package_activity
