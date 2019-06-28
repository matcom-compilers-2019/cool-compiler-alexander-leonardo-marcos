import copy

from . import cilast as cil
from . import coolast as ast
from . import visitor
from .scope import VariableInfo
from . import coolutils
from .context import Context
from pprint import pprint

class Cool2CilVisitor:
    def __init__(self, semantic_scope):
        # Handle current program
        self.dottypes = []
        self.dotdata = []
        self.dotcode = []
        self.globalvars = []

        # Handle current function
        self.current_function_name = ""
        self.local_index = 0  # This solves the variable scopes
        self.instructions = []
        
        # Holds the maps: 
        # * method name => offset in the class 
        # * var name => offset in the function
        self.context = Context()

        # Handle current class
        self.current_class_name = ""
        self.attributes = []
        self.methods = []

        # Handle internal names
        self.internal_count = 0
        self.internal_f_count = 0
        self.internal_l_count = 0

        self.semantic_scope = semantic_scope

    # ======================================================================
    # =[ UTILS ]============================================================
    # ======================================================================

    def build_internal_fname(self):
        fname = f'f{self.internal_f_count}'
        self.internal_f_count += 1
        return fname

    def build_method_name(self):
        mname = f'{self.current_class_name}_{self.current_function_name}'
        return mname

    def define_internal_lname(self):
        lname = f'{self.internal_l_count}_LABEL'
        self.internal_l_count += 1
        return lname

    def build_internal_vname(self, vname):
        vname = f'{self.internal_count}_{self.current_function_name}_{vname}'
        self.internal_count += 1
        return vname

    def define_internal_local(self):
        vinfo = VariableInfo('internal')
        return self.register_local(vinfo)

    def register_local(self, vinfo):
        vinfo.name = self.build_internal_vname(vinfo.name)
        vinfo.holder = len(self.globalvars)
        local_node = cil.CILLocal(vinfo)
        self.globalvars.append(local_node)
        # print("global")
        # print(self.globalvars)
        return vinfo

    def register_instruction(self, instruction_type, *args):
        instruction = instruction_type(*args)
        self.instructions.append(instruction)
        return instruction

    def register_func(self, mname):
        # print("Register Function")
        func = cil.CILFunction(mname, self.instructions.copy())
        
        # Handle localvars
        func.localvars = self.globalvars[self.local_index:]
        self.local_index = len(self.globalvars)

        # Update the context with the new names
        for index, local in enumerate(func.localvars):
            self.context.add_var(local.vinfo.name, index)
        
        self.dotcode.append(func)
        return func

    def register_type(self):
        ttype = cil.CILType(self.current_class_name, self.attributes, self.methods.copy())
        self.context.add_tag(self.current_class_name)
        self.dottypes.append(ttype)
        return ttype

    def register_data(self, value):
        vname = f'data_{len(self.dotdata)}'
        data_node = cil.CILData(vname, value)
        self.dotdata.append(data_node)
        return data_node

    def build_ctr(self, attrs):
        # Build constructor
        self.current_function_name = "ctr"
        self.instructions.clear()

        self.register_instruction(cil.CILParam, VariableInfo('self'))
        for index, attr in enumerate(attrs):
            attr_node = self.visit(attr)
            self.context.add_attribute(attr_node, index)
            attr_node.attribute = index
            self.instructions.append(attr_node)
            # ctr.append(attr_node)
        self.register_instruction(cil.CILReturn, VariableInfo('self'))

        ctr_name = self.build_method_name()
        func_node = self.register_func(ctr_name)
        func_node.param_count = 1
        # ctr_func = cil.CILFunction(ctr_name, self.instructions.copy())
        # self.dotcode.append(ctr_func)

        self.methods.append(cil.CILMethod(ctr_name))

        self.context.add_mf(ctr_name, ctr_name)

    def build_entry(self):
        self.instructions.clear()

        main_holder = self.register_local(VariableInfo('instance'))
        self.register_instruction(cil.CILAllocate, main_holder, "Main")
        
        self.register_instruction(cil.CILArg, main_holder)
        self.register_instruction(cil.CILCall, main_holder, 'Main_ctr')        

        self.register_instruction(cil.CILArg, main_holder)
        temp = self.define_internal_local()
        self.register_instruction(cil.CILVCall, temp, "Main", "Main_main")
        
        self.register_instruction(cil.CILReturn, 0)

        self.current_function_name = "main"
        # entry_name = self.build_internal_fname()
        func_node = self.register_func(self.current_function_name)
        func_node.param_count = 1

    # ======================================================================

    # ======================================================================
    # =[ VISIT ]============================================================
    # ======================================================================

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.Program)
    def visit(self, node: ast.Program):
        """
        Every program in cool has a `Main` class and a `main` method.
        Every program in cil should have an `entrypoint` method which is to be run to start the program.
        """
        ttypes = self.semantic_scope.get_types_dict().values()
        klasses = [klass for klass in ttypes if not klass in node.classes]
        for klass in klasses:
            # print(klass.parent)
            self.visit(klass)

        # We register the entrypoint here.
        self.build_entry()

        self.result = cil.CILProgram(self.dottypes, self.dotdata, self.dotcode)

    @visitor.when(ast.Class)
    def visit(self, node: ast.Class):
        # Update current class name
        self.current_class_name = node.name

        # Clear old values
        self.attributes.clear()
        self.methods.clear()


        # print(node.name)
        # print(node.inherited)
        attrs = []
        for feature in node.features:
            if isinstance(feature, ast.ClassAttribute):
                attrs.append(feature)
        
        # Build constructor
        self.build_ctr(attrs)

        # pprint(node.name)
        # pprint(node.merged)
        for index, func in enumerate(node.merged):
            # print(func.name)
            mnode = self.visit(func)
            mnode.holder = index
            self.context.add_func(mnode.name, index + 2)

        ttype = self.register_type()
        return ttype

    @visitor.when(ast.ClassMethod)
    def visit(self, node: ast.ClassMethod):
        # This visit is divided in two:
        #   * The addition of the method to the current type
        #   * The addition of a new function to dotcode
        self.current_function_name = node.name
        mname = self.build_method_name()

        # print(self.semantic_scope.get_type(self.current_class_name).name)
        # print(node.name)
        # print(self.semantic_scope.get_type(self.current_class_name).inherited)

        if node in self.semantic_scope.get_type(self.current_class_name).inherited:
            current = self.semantic_scope.get_type(self.current_class_name).parent
            while current is not None:
                current_type = self.semantic_scope.get_type(current)
                for feat in current_type.features:
                    if isinstance(feat, ast.ClassMethod) and current_type.is_method_in_features(feat.name):
                        self.context.add_mf(mname, f'{current_type.name}_{node.name}')
                        break
                current = current_type.parent
        else:
            self.context.add_mf(mname, mname)

        # fname = self.build_internal_fname()

        # Method addition
        mnode = cil.CILMethod(mname)
        mnode.holder = node.holder
        self.context.add_func(mname, mnode.holder)
        self.methods.append(mnode)
        # print("AAAA")
        # print([x.mname for x in self.methods])

        # Register the function in dotcode if it's new
        if self.context.mmap[mname] == mname:
            # Function addition
            # Clean instruction list
            self.instructions.clear()

            self.register_instruction(cil.CILParam, VariableInfo('self'))
            for index, param in enumerate(node.formal_params):
                param_vinfo = self.visit(param)
                param_vinfo.holder = index

            # Method body
            builtins = ["String", "Int", "Bool", "IO", "Object"]
            if not self.current_class_name in builtins \
                and not node.name.startswith('String') \
                and not node.name.startswith('Int') \
                and not node.name.startswith('Bool') \
                and not node.name.startswith('IO') \
                and not node.name.startswith('Object'):
                vinfo = self.visit(node.body)
                # print("Method body vinfo", vinfo.name)
                self.register_instruction(cil.CILReturn, vinfo)

            # print(return_val)
            func_node = self.register_func(mname)
            func_node.param_count = len(node.formal_params)

        return node

    @visitor.when(ast.ClassAttribute)
    def visit(self, node: ast.ClassAttribute):
        self.attributes.append(node.name)

        if node.init_expr:
            vsrc = self.visit(node.init_expr)
        else:  # Init with default of the type
            default_init = coolutils.default(node.attr_type)
            vsrc = self.visit(default_init) if str(default_init) != "void" else "void"
        self_vinfo = VariableInfo('self')
        self_vinfo.holder = 0
        return cil.CILSetAttrib(self_vinfo, node.name, vsrc)

    @visitor.when(ast.FormalParameter)
    def visit(self, node: ast.FormalParameter):
        param_vinfo = VariableInfo(node.name)
        self.register_instruction(cil.CILParam, param_vinfo)
        return param_vinfo

    @visitor.when(ast.Object)
    def visit(self, node: ast.Object):
        for lvar in self.globalvars[self.local_index:]:
            if lvar.vinfo.name.endswith(node.name):
                return lvar.vinfo
        else:
            var = self.register_local(VariableInfo(node.name))
            return var

        # print("node.name", node.name)
        # print("localvars", list(map(lambda x: x.vinfo.name, self.globalvars[self.local_index:])))
        # if node.name in map(lambda x: x.vinfo.name, self.globalvars[self.local_index:]):  # It's a local var
        #     return self.context.lmap[node.name]
        # else:  # It's a self property
        #     vattr = self.define_internal_local()
        #     self.register_instruction(cil.CILGetAttrib, vattr, VariableInfo('self'), node.name)
        #     return vattr
        # var = self.define_internal_local()


    @visitor.when(ast.Self)
    def visit(self, node: ast.Self):
        """
        Load to a variable the location of `self` in memory.
        This has a dedicated CIL node since we have to look in the stack
        for the first param, which is where `self` will be,
        the src is always the same.
        lw $a0, 0($sp)
        """
        # dummy_node = self.register_instruction(cil.CILDummy, 'lw $a0, 4($sp)')
        self_vinfo = VariableInfo('self')
        self_vinfo.holder = 1
        return self_vinfo

    @visitor.when(ast.Integer)
    def visit(self, node: ast.Integer):
        # print('Integer')
        # dummy_node = self.register_instruction(cil.CILDummy, f'li $a0, {node.content}')
        boxed = self.define_internal_local()
        self.register_instruction(cil.CILAllocate, boxed, "Int")
        self.register_instruction(cil.CILSetAttrib, boxed, 0, node.content)
        return boxed

    @visitor.when(ast.String)
    def visit(self, node: ast.String):
        # for index, data_node in enumerate(self.dotdata):
        #     if node.content == data_node.value:
        #         data_name = data_node.vname
        # else:
        #     new_node = self.register_data(node.content)
        #     data_name = new_node.vname

        # dummy_node = self.register_instruction(cil.CILDummy, f'la $a0, {data_name}')
        data_node = self.register_data(node.content)
        boxed_string = self.define_internal_local()
        boxed_int = self.define_internal_local()
        self.register_instruction(cil.CILAllocate, boxed_int, "Int")
        self.register_instruction(cil.CILSetAttrib, boxed_int, 0, len(node.content))

        self.register_instruction(cil.CILAllocate, boxed_string, "String")
        self.register_instruction(cil.CILSetAttrib, boxed_string, 0, boxed_int)
        self.register_instruction(cil.CILSetAttrib, boxed_string, 1, data_node)

        return boxed_string

    @visitor.when(ast.Boolean)
    def visit(self, node: ast.Boolean):
        # dummy_node = self.register_instruction(cil.CILDummy, f'li $a0, {1 if node.content == True else 0}')
        boxed = self.define_internal_local()
        self.register_instruction(cil.CILAllocate, boxed, "Bool")
        self.register_instruction(cil.CILSetAttrib, boxed, 0, 1 if node.content else 0)
        return boxed
        
    @visitor.when(ast.NewObject)
    def visit(self, node: ast.NewObject):
        vinfo = self.define_internal_local()
        self.register_instruction(cil.CILAllocate, vinfo, node.type)
        self.register_instruction(cil.CILArg, VariableInfo('self'))
        self.register_instruction(cil.CILCall, vinfo, f'{node.type}_ctr')
        return vinfo

    @visitor.when(ast.IsVoid)
    def visit(self, node: ast.IsVoid):
        dest_vinfo = self.define_internal_local()
        vinfo = self.visit(node.expr)
        self.register_instruction(cil.CILTypeOf, ttype, vinfo)
        self.register_instruction(cil.CILEqual, dest_vinfo, ttype, "void")
        return dest_vinfo

    @visitor.when(ast.Assignment)
    def visit(self, node: ast.Assignment):
        """
        There are three ways of making an assignment.
            i. By declaring an attribute.
            ii. By declaring inside a let.
            iii. Just assigning a value.
        
        The first two share the syntax, but the third doesn't.
        In this node we don't have to generate a LOCAL CIL node,
        because to make this kind of assignment(iii) the identifier
        should be declared from beforehand.
        
        First, check if the source is in `localvars`,
        if not, check if it's in the function arguments.

        Repeat with destination.        
        """
        source = self.visit(node.expr)
        vinfo = self.visit(node.identifier)
        for lvar in self.globalvars[self.local_index:]:
            if lvar.vinfo.name.endswith(vinfo.name):
                self.register_instruction(cil.CILAssign, lvar.vinfo, source)
                return lvar
        else:
            # print(node.identifier, node.identifier.name)

            self.register_instruction(cil.CILSetAttrib, VariableInfo('self'), vinfo, source)
            return node.identifier


        # if source.name in map(lambda x: x.vinfo.name, self.globalvars[self.local_index:]):  # It's a local var
        #     # offset_src = self.context.lname[source]
        #     # print(f'node.identifier =>', node.identifier)
        #     # print(f'self.context.lmap[node.identifier.name] =>', self.context.lmap[node.identifier.name])
        #     # vdest = self.define_internal_local()
        #     # self.register_instruction(cil.CILAssign, self.context.lmap[node.identifier.name], source)
        #     self.register_instruction(cil.CILAssign, node.identifier, source)
        #     # self.register_instruction(cil.CILDummy, f'lw $t0, {offset_src * -4}')
        # else:  # It's a property of `self`
        #     # offset_src = self.context.lname[source]
        #     self.register_instruction(cil.CILSetAttrib, VariableInfo('self'), node.identifier.name, source.name)
        #     # self.register_instruction(cil.CILDummy, f'lw $a0, {offset_src * 4}')

        # self.register_instruction(cil.CILAssign, self.context.lmap[node.identifier.name], source)
        # return node.identifier

    @visitor.when(ast.Block)
    def visit(self, node: ast.Block):
        # print('Block')
        vinfo = 0
        for expr in node.expr_list:
            vinfo = self.visit(expr)
        return vinfo

    @visitor.when(ast.DynamicDispatch)
    def visit(self, node: ast.DynamicDispatch):
        # # Save current frame pointer
        # self.register_instruction(cil.CILDummy, 'sw $fp 0($sp)')
        
        # Generate code for each of the params and push them
        for index, arg in enumerate(reversed(node.arguments)):
            vinfo = self.visit(arg)
            vinfo.holder = index
            arg_node = self.register_instruction(cil.CILArg, vinfo)
    
        instance = self.visit(node.instance)  
        
        # This is going to be param `self`
        self.register_instruction(cil.CILArg, VariableInfo('self'))

        # Here we have to compute the type, which is done using TYPEOF
        vtype = self.define_internal_local()
        self.register_instruction(cil.CILTypeOf, vtype, instance)
        vresult = self.define_internal_local()
        # print(node)
        # print(node.method)

        mname = f'{node.instance.return_type}_{node.method}'
        self.register_instruction(cil.CILVCall, vresult, vtype, mname)
        return vresult

    @visitor.when(ast.StaticDispatch)
    def visit(self, node: ast.StaticDispatch):
        # # Save current frame pointer
        # self.register_instruction(cil.CILDummy, 'sw $fp 0($sp)')

        # Generate code for each of the params and push them
        for index, arg in enumerate(list(reversed(node.arguments))):
            vinfo = self.visit(arg)
            vinfo.holder = index
            arg_node = self.register_instruction(cil.CILArg, vinfo)

        vresult = self.define_internal_local()
        # print(node.method)
        self.register_instruction(cil.CILVCall, vresult, node.dispatch_type, node.method)
        return vresult

    @visitor.when(ast.Let)
    def visit(self, node: ast.Let):
        # print('Let')
        for declaration in node.declaration_list:
            self.visit(declaration)

        vinfo = self.visit(node.body)
        # print(vinfo)

        return vinfo

    @visitor.when(ast.Declaration)
    def visit(self, node: ast.Declaration):
        # print('Declaration')
        vdest = self.visit(node.identifier)
        # identifier = self.register_local(node.identifier)
        
        if node.expression:
            vsrc = self.visit(node.expression)
        else:
            default_init = coolutils.default(node.ttype)
            vsrc = self.visit(default_init) if str(default_init) != "void" else VariableInfo("void")
        assert vsrc != None, "`vsrc` is None inside `Declaration` visit"

        self.register_instruction(cil.CILAssign, vdest, vsrc)
        return vdest

    @visitor.when(ast.If)
    def visit(self, node: ast.If):
        """
        LOCAL predicate_vinfo;
        LOCAL if_result;

        predicate_vinfo = <node.predicate>;
        if predicate_vinfo GOTO then_label;
        if_result = <node.else_body>;
        GOTO continue_label;
        LABEL then_label;
        if_result = <node.then_body>;
        LABEL continue_label;
        """
        then_label = self.define_internal_lname()
        continue_label = self.define_internal_lname()

        predicate_vinfo = self.visit(node.predicate)
        self.register_instruction(cil.CILGotoIf, predicate_vinfo, then_label)
        self.visit(node.else_body)
        self.register_instruction(cil.CILGoto, continue_label)
        self.register_instruction(cil.CILLabel, then_label)
        self.visit(node.then_body)
        self.register_instruction(cil.CILLabel, continue_label)

    # TODO: How do I return void??????? My head is spinning! Is it just a 0?
    # TODO: I can optimize this code! Nevermind, the line I can save is spent somewhere else :(.
    @visitor.when(ast.WhileLoop)
    def visit(self, node: ast.WhileLoop):
        """
        LOCAL predicate_vinfo;

        LABEL while_label
        predicate_vinfo = <node.predicate>;
        if predicate_vinfo GOTO loop_label;
        GOTO pool_label;
        LABEL loop_label;
        <node.body>;
        GOTO while_label;
        LABEL pool_label;
        TODO: return void here!
        """
        while_label = self.define_internal_lname()
        loop_label = self.define_internal_lname()
        pool_label = self.define_internal_lname()

        self.register_instruction(cil.CILLabel, while_label)
        predicate_vinfo = self.visit(node.predicate)
        self.register_instruction(cil.CILGotoIf, predicate_vinfo, loop_label)
        self.register_instruction(cil.CILGoto, pool_label)
        self.register_instruction(cil.CILLabel, loop_label)
        self.visit(node.body)
        self.register_instruction(cil.CILGoto, while_label)
        self.register_instruction(cil.CILLabel, pool_label)
        return 0  # void?????

    @visitor.when(ast.Case)
    def visit(self, node: ast.Case):
        pass

    @visitor.when(ast.Action)
    def visit(self, node: ast.Action):
        pass

    @visitor.when(ast.IntegerComplement)
    def visit(self, node: ast.IntegerComplement):
        vinfo = self.visit(node.integer_expr)
        dest = self.define_internal_local()
        self.register_instruction(cil.CILMinus, dest, 0, vinfo)
        return dest

    @visitor.when(ast.BooleanComplement)
    def visit(self, node: ast.BooleanComplement):
        vinfo = self.visit(node.expr)
        dest = self.define_internal_local()
        self.register_instruction(cil.CILMinus, dest, 1, vinfo)
        return dest

    @visitor.when(ast.Addition)
    def visit(self, node: ast.Addition):
        left_vinfo = self.visit(node.first)
        right_vinfo = self.visit(node.second)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILPlus, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Subtraction)
    def visit(self, node: ast.Subtraction):
        left_vinfo = self.visit(node.first)
        right_vinfo = self.visit(node.second)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILMinus, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Multiplication)
    def visit(self, node: ast.Multiplication):
        left_vinfo = self.visit(node.first)
        right_vinfo = self.visit(node.second)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILStar, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Division)
    def visit(self, node: ast.Division):
        left_vinfo = self.visit(node.first)
        right_vinfo = self.visit(node.second)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILDiv, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Equal)
    def visit(self, node: ast.Equal):
        first_vinfo = self.visit(node.first)
        second_vinfo = self.visit(node.second)
        vinfo = self.define_internal_local()
        self.register_instruction(cil.CILEqual, vinfo, first_vinfo,
                                  second_vinfo)
        return vinfo

    @visitor.when(ast.LessThan)
    def visit(self, node: ast.LessThan):
        first_vinfo = self.visit(node.first)
        second_vinfo = self.visit(node.second)
        vinfo = self.define_internal_local()
        self.register_instruction(cil.CILLessThan, vinfo, first_vinfo,
                                  second_vinfo)
        return vinfo

    @visitor.when(ast.LessThanOrEqual)
    def visit(self, node: ast.LessThanOrEqual):
        first_vinfo = self.visit(node.first)
        second_vinfo = self.visit(node.second)
        vinfo = self.define_internal_local()
        self.register_instruction(cil.CILLessThanOrEqual, vinfo, first_vinfo,
                                  second_vinfo)
        return vinfo
