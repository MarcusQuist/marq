import sys

sys.version
import pathlib
from pathlib import Path
from node_settings import get_color, scale_value
from churn import get_commit_activity, get_lines_of_code_activity

# Kør i CMD
# pip3 install gitpython
# pip3 install pyvis
# pip3 install pydriller
# git clone https://github.com/zeeguu/api.git


# ========================================================================
# Let's declare a var for the path where we're going to download a repository
# Warning: this must end in /
CODE_ROOT_FOLDER = "api/"

color_legend = [(0, 500, 'blue'), (500, 1000, 'lightblue'), (1000, 1500, 'orange'), (1500, 2000, 'red')]


def file_path(file_name):
    return CODE_ROOT_FOLDER + file_name


assert file_path("zeeguu/core/model/user.py") == "api/zeeguu/core/model/user.py"


# ========================================================================
# extracting a module name from a file name
def module_name_from_file_path(full_path):
    # e.g. ../core/model/user.py -> zeeguu.core.model.user

    file_name = full_path[len(CODE_ROOT_FOLDER) :]
    file_name = file_name.replace("/__init__.py", "")
    file_name = file_name.replace("/", ".")
    file_name = file_name.replace("\\", ".")
    file_name = file_name.replace(".py", "")
    return file_name


assert "zeeguu.core.model.user" == module_name_from_file_path(
    file_path("zeeguu/core/model/user.py")
)


# ========================================================================
# naïve way of extracting imports using regular expressions
import re

# we assume that imports are always at the
def import_from_line(line):
    # regex patterns used
    #   ^  - beginning of line
    #   \S - anything that is not space
    #   +  - at least one occurrence of previous
    #  ( ) - capture group (read more at: https://pynative.com/python-regex-capturing-groups/)
    try:
        y = re.search("from (\S+)", line)
        if not y:
            y = re.search("^import (\S+)", line)
        return y.group(1)
    except:
        return None
    
# ========================================================================
def top_level_package(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[:depth])


# ========================================================================
# extracts all the imported modules from a file
# returns a module of the form zeeguu_core.model.bookmark, e.g.
def imports_from_file(file):
    all_imports = []

    lines = [line for line in open(file)]

    for line in lines:
        imp = import_from_line(line)

        if imp:
            all_imports.append(imp)

    return all_imports


# ========================================================================
# Extracts only the interesting modules - modules starting with zeeguu and which are not use for test cases
def interesting_module(module_name):
    return module_name.startswith("zeeguu") and not "test" in module_name

# ========================================================================
# Extracts only core modules
def core_module(module_name):
    return module_name.startswith("zeeguu.core")

# ========================================================================
# Extracts only api modules
def api_module(module_name):
    return module_name.startswith("zeeguu.api")

# ========================================================================
# Extracts only model modules
def model_module(module_name):
    return module_name.startswith("zeeguu.core.model")

# ========================================================================
# Creates the first graph with all intereseting modules represented
from pyvis.network import Network
from IPython.core.display import HTML

def dependencies_graph():
    files = Path("./api").rglob("*.py")

    G = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black",
        select_menu=True,
    )

    for file in files:
        file_path = str(file)

        module_name = module_name_from_file_path(file_path)


        if not interesting_module(module_name):
            continue
        if module_name not in G.nodes:
            G.add_node(module_name)

        for _import in imports_from_file(file_path):
            if _import not in G.nodes and interesting_module(_import):
                G.add_node(_import)
                G.add_edge(module_name, _import)

    return G


# ========================================================================
# Creates the abstracted graph containing only the defined interesting top level modules

def abstracted_to_top_level(G, depth=1, getCore = False, getApi = False, getModel = False):
    package_activity = get_commit_activity(depth)
    lines_activity = get_lines_of_code_activity(depth)

    aG = Network(
        height="800px",
        width="100%",
        directed=True,
        font_color="black",
        bgcolor="#ffffff",
        select_menu=True,
    )
    for node in G.nodes:
        aG.add_node(top_level_package(node["id"], depth))
    for edge in G.edges:
        src = top_level_package(edge["from"], depth)
        dst = top_level_package(edge["to"], depth)

        if src != dst:
            aG.add_edge(src, dst)

    filteredAg = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black",
        select_menu=True,
    )

    # SET EDGE BEHAVIOR
    # NOTE: When using 'dynamic', the edges will have an invisible support node guiding the shape. 
    # This node is part of the physics simulation. Default is set to 'continous'.
    filteredAg.set_edge_smooth('discrete')  


    # Creates a new set of nodes and edges containing to make possible a way to count the edges,
    # and subsequently give them a specific width. Edges with the same source and target are only added once.
    # The witdh is determined by the number of times you meet an edge with the same source and target - which is captured in a dictionary
    new_nodes = set()
    new_edges = []
    for edge in aG.edges:
        source = edge["from"]
        target = edge["to"]
        if(getCore):
            top_level_package_name_from = lines_activity[top_level_package(source, depth)]
            top_level_package_name_to = lines_activity[top_level_package(target, depth)]
            if(core_module(source)):
                new_nodes.add(source)   
            if(core_module(target)):
                new_nodes.add(target)   
            if(core_module(source) and core_module(target)):
                new_edges.append(edge)
        if(getApi):
            top_level_package_name_from = lines_activity[top_level_package(source, depth)]
            top_level_package_name_to = lines_activity[top_level_package(target, depth)]
            if(api_module(source)):
                new_nodes.add(source)   
            if(api_module(target)):
                new_nodes.add(target)   
            if(api_module(source) and api_module(target)):
                new_edges.append(edge)
        if(getModel):
            if(model_module(source)):
                new_nodes.add(source)   
            if(model_module(target)):
                new_nodes.add(target)   
            if(model_module(source) and model_module(target)):
                new_edges.append(edge)
        if(getApi == False and getCore == False and getModel == False):
            new_nodes.add(edge["from"])
            new_nodes.add(edge["to"])
            new_edges.append(edge)
    zero_nodes = []

    churn_upper_bound = 999
    min_lines_of_code = 0
    min_commit_count = 0

    if(getCore):
        churn_upper_bound = 300
    if(getApi):
        churn_upper_bound = 125

    for node in aG.nodes:
        if node["id"] in new_nodes:
            top_level_package_name = top_level_package(node["id"], depth)
            
            lines = lines_activity[top_level_package_name]
            # lines = 2
            if lines == 0:
                zero_nodes.append(node["id"])
                continue
            color = get_color(package_activity[top_level_package_name], churn_upper_bound)
            size = scale_value(lines)
            mass = scale_value(lines_activity[top_level_package_name]) * 0.3
            # color = 3
            # size = 3
            mass = 100
            label = "{}\n(LOC: {} C: {})".format(top_level_package_name, lines, package_activity[top_level_package_name])
            filteredAg.add_node(node["id"], color=color, size=size, mass=mass, label=label)

    edge_counts = {}
    for edge in new_edges:
        source = edge["from"]
        target = edge["to"]
        key = (source, target)

        if key in edge_counts:
            edge_counts[key] += 1
        else:
            edge_counts[key] = 1
            if source in zero_nodes or target in zero_nodes:
                continue
            filteredAg.add_edge(edge["from"], edge["to"], arrowStrikethrough = False, color="black")

    for edge in filteredAg.edges:
        source = edge["from"]
        target = edge["to"]
        key = (source, target)

        if key in edge_counts:
            edge["width"] = edge_counts[key] * 0.05
            edge["label"] = str(edge_counts[key])

    return filteredAg

# ========================================================================
from IPython.display import display, HTML

# ========================================================================
# Color bar
# ========================================================================
color_legend = [(0, 500, 'blue'), (500, 1000, 'lightblue'), (1000, 1500, 'orange'), (1500, 2000, 'red')]

# ========================================================================
# Dependencies graph containing all files in the repository
# ========================================================================
DG = dependencies_graph()
DG.toggle_physics(True)
DG.prep_notebook()
DG.force_atlas_2based()
DG.show_buttons(filter_=["physics"])
DG.show("./page.html")

# ========================================================================
# Abstracted dependencies graph containing only the 2 top level files in the repository (zeeguu, zeeguu.core, zeeguu.api)
# ========================================================================
ADG = abstracted_to_top_level(DG, 2)
ADG.toggle_physics(False)
ADG.prep_notebook()
ADG.force_atlas_2based()
ADG.show_buttons(filter_=["physics"])
ADG.show("./ADG.html")

# ========================================================================
# Abstracted dependencies graph containing only the 3 top level files in the repository
# ========================================================================
# ADG3 = abstracted_to_top_level(DG, 3)
# ADG3.toggle_physics(False)
# ADG3.prep_notebook()
# ADG3.force_atlas_2based()
# ADG3.show_buttons(filter_=["physics"])
# ADG3.show("./ADG3.html")

# ========================================================================
# Abstracted dependencies graph containing only the 3 top level files in the repository of the core
# ========================================================================
coreADG = abstracted_to_top_level(DG, 3, True, False, False)
coreADG.toggle_physics(False)
coreADG.prep_notebook()
coreADG.force_atlas_2based()
coreADG.show_buttons(filter_=["physics"])
coreADG.show("./coreADG.html")

# ========================================================================
# Abstracted dependencies graph containing only the 4 top level files in the repository of the api
# ========================================================================
coreADG = abstracted_to_top_level(DG, 4, False, True, False)
coreADG.toggle_physics(False)
coreADG.prep_notebook()
coreADG.force_atlas_2based()
coreADG.show_buttons(filter_=["physics"])
coreADG.show("./apiADG.html")

# ========================================================================
# Abstracted dependencies graph containing only the 4 top level files in the repository of the model
# ========================================================================
coreADG = abstracted_to_top_level(DG, 4, False, False, True)
coreADG.toggle_physics(False)
coreADG.prep_notebook()
coreADG.force_atlas_2based()
coreADG.show_buttons(filter_=["physics"])
coreADG.show("./modelADG.html")


