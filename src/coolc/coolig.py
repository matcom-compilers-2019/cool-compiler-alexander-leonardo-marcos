from collections import defaultdict
from . import coolast as ast
from . import visitor


class InheritanceGraphVisitor:
    """
    - The graph must be a tree.
    - 'Object' is the root of the tree.
    - It is an error to inherit from 'String', 'Int' or 'Bool' (Redefinition of builtin classes is checked in cooltypes)
    """

    def __init__(self, class_list):
        self.class_list = class_list
        # self.edges = []
        self.adjacency_dict = {}
        self.build_adjacency_dict()
        self.in_degrees = defaultdict(int)

    # Sort of DFS to check for cycles.
    def check_graph(self, errors):
        # Testing purposes only
        # self.adjacency_dict["Object"].append("Object")  # Passed
        # self.adjacency_dict["String"].append("Temp")  # Passed

        def dfs(node):
            visited.append(node)
            valid = 1
            for child in self.adjacency_dict[node]:
                if node in sealed_types:
                    errors.append(f"Type <{child}> inherits from <{node}>, which is sealed in Cool!")
                    valid &= 0

                if child in visited:
                    errors.append(f"There is a cycle containing <{child}>!")
                    return 0
                valid &= dfs(child)
            return valid

        visited = []
        sealed_types = ['Int', 'Bool', 'String']

        return dfs("Object") & self.visit_all(dfs, visited)

    def build_adjacency_dict(self):
        for klass in self.class_list:
            if klass.parent is not None:
                if self.adjacency_dict.get(klass.parent) is None:
                    self.adjacency_dict[klass.parent] = []
                if self.adjacency_dict.get(klass.name) is None:
                    self.adjacency_dict[klass.name] = []
                self.adjacency_dict[klass.parent].append(klass.name)

    def visit_all(self, dfs, visited: list) -> bool:
        valid = 1
        for klass in self.class_list:
            if klass.name not in visited:
                valid &= dfs(klass.name)
        return valid

    def build_degrees(self):
        for parent, children in self.adjacency_dict.items():
            for child in children:
                self.in_degrees[child] += 1
        self.in_degrees['Object'] = 0

    def topological_sort(self):
        def aux(in_degrees):
            # print(in_degrees.items())
            if not len(in_degrees):
                return []

            in_sorted = sorted(in_degrees.items(), key=lambda x: x[1])
            for child in self.adjacency_dict[in_sorted[0][0]]:
                in_degrees[child] -= 1
            
            in_degrees.pop(in_sorted[0][0])
            return [in_sorted[0][0]] + aux(in_degrees) 

        self.build_degrees()
        in_degrees = self.in_degrees.copy()
        return aux(in_degrees) 


    def handle_inheritance(self, scope):
        klasses = scope.get_types_dict()
        for name in self.topological_sort():
            if name == "Object":
                continue
            
            node = klasses[name]
            parent = klasses[node.parent]

            node.inherited += [x for x in parent.inherited]
            node.inherited += [x for x in parent.features \
                if isinstance(x, ast.ClassMethod) \
                    and x.name not in map(lambda y: y.name, node.inherited)]

            node.merged += node.inherited.copy()
            # node.merged += [x for x in node.features if isinstance(x, ast.ClassMethod)]
            node.merged += [x for x in node.features \
                if isinstance(x, ast.ClassMethod) \
                    and x.name not in map(lambda y: y.name, node.inherited)]
