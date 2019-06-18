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
        vinfo.vmholder = len(self.globalvars)
        local_node = cil.CILLocal(vinfo)
        self.globalvars.append(local_node)
        # print("global")
        # print(self.globalvars)
        return vinfo

    def register_instruction(self, instruction_type, *args):
        instruction = instruction_type(*args)
        self.instructions.append(instruction)
        return instruction

    def register_func(self, fname, mname):
        # print("Register Function")
        func = cil.CILFunction(mname, self.instructions)
        
        # Handle localvars
        func.localvars = self.globalvars[self.local_index:]
        self.local_index = len(self.globalvars)

        # Update the context with the new names
        for index, local in enumerate(func.localvars):
            self.context.add_var(local.value.name, index)
        
        # Update the context with the function name
        self.context.add_mf(mname, fname)

        self.dotcode.append(func)
        return func

    def register_type(self):
        ttype = cil.CILType(self.current_class_name, self.attributes, self.methods)
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
        ctr = []
        for index, attr in enumerate(attrs):
            attr_node = self.visit(attr)
            self.context.add_attribute(attr_node, index)
            ctr.append(attr_node)
        ctr.append(cil.CILReturn())

        self.current_function_name = "ctr"
        fname = self.build_internal_fname()
        ctr_name = self.build_method_name()
        ctr_func = cil.CILFunction(ctr_name, ctr)
        self.dotcode.append(ctr_func)

        self.methods.append(cil.CILMethod(ctr_name))

        self.context.add_mf(ctr_name, fname)

    def build_entry(self):
        self.register_instruction(cil.CILAllocate, "Main")
        self.register_instruction(cil.CILArg)
        self.register_instruction(cil.CILCall, f'Main_ctr')        
        self.register_instruction(cil.CILArg)
        self.register_instruction(cil.CILVCall, "Main", "Main_main")
        
        self.current_function_name = "entry"
        # entry_name = self.build_internal_fname()
        self.register_func("main", self.current_function_name)

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
        builtins = self.semantic_scope.get_types_dict().values()
        klasses = [klass for klass in builtins if not klass in node.classes]
        # Maybe sort the types before visiting them?
        for klass in klasses:
            # print(klass)
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

        attrs, funcs = [], []
        for feature in node.features:
            if isinstance(feature, ast.ClassMethod):
                # print("!!!")
                # print(self.current_class_name)
                # print(feature)
                funcs.append(feature)
            else:
                attrs.append(feature)
        
        # Build constructor
        self.build_ctr(attrs)

        # pprint(funcs)
        for index, func in enumerate(funcs):
            print(func)
            func_node = self.visit(func)
            self.context.add_func(func_node.fname, index)

        # TODO: What if we have a constructor which calls a ctor which calls the first ctor? Python gives
        # recurison depth exceeded, of course, does C# detect this at compile time?

        ttype = self.register_type()
        # print(ttype)
        return ttype

    @visitor.when(ast.ClassMethod)
    def visit(self, node: ast.ClassMethod):
        # This visit is divided in two:
        #   * The addition of the method to the current type
        #   * The addition of a new function to dotcode
        self.current_function_name = node.name
        mname = self.build_method_name()
        fname = self.build_internal_fname()

        # Method addition
        self.methods.append(cil.CILMethod(mname))

        # Function addition
        # Clean instruction list
        self.instructions.clear()

        # Method body
        self.visit(node.body)
        # print(return_val)

        # Register the function in dotcode
        func = self.register_func(fname, mname)
        func.param_count = len(node.formal_params)        
        return func

    @visitor.when(ast.ClassAttribute)
    def visit(self, node: ast.ClassAttribute):
        # Check we're not cleaning and losing ctor instructions!
        self.attributes.append(node.name)

        if node.init_expr:
            name = self.visit(node.init_expr)
        else:  # Init with default of the type
            name = coolutils.default(node.attr_type)
        return cil.CILSetAttrib("self", node.name, name)

    @visitor.when(ast.FormalParameter)
    def visit(self, node: ast.FormalParameter):
        param_node = self.register_instruction(cil.CILParam, node.name)
        return param_node

    @visitor.when(ast.Object)
    def visit(self, node: ast.Object):
        return node.name

    @visitor.when(ast.Self)
    def visit(self, node: ast.Self):
        """
        Load to a variable the location of `self` in memory.
        This has a dedicated CIL node since we have to look in the stack
        for the first param, which is where `self` will be,
        the src is always the same.
        lw $a0, 0($sp)
        """
        dummy_node = self.register_instruction(cil.CILDummy, 'lw $a0, 4($sp)')
        return dummy_node

    @visitor.when(ast.Integer)
    def visit(self, node: ast.Integer):
        # print('Integer')
        dummy_node = self.register_instruction(cil.CILDummy, f'li $a0, {node.content}')
        return dummy_node

    @visitor.when(ast.String)
    def visit(self, node: ast.String):
        """
        If the String is already in the .DATA section, we won't register it
        again. We just return the name we gave it, which includes its offset.
        We have to load the starting address of .DATA plus the offset of this
        string. But most of this is MIPS.
        la $a0, string_address
        """
        for index, data_node in enumerate(self.dotdata):
            if node.content == data_node.value:
                data_name = data_node.vname
        else:
            new_node = self.register_data(node.content)
            data_name = new_node.vname

        dummy_node = self.register_instruction(cil.CILDummy, f'la $a0, {data_name}')
        return dummy_node

    @visitor.when(ast.Boolean)
    def visit(self, node: ast.Boolean):
        dummy_node = self.register_instruction(cil.CILDummy, f'li $a0, {1 if node.content == True else 0}')
        return dummy_node
        
    @visitor.when(ast.NewObject)
    def visit(self, node: ast.NewObject):
        self.register_instruction(cil.CILAllocate, node.new_type)
        self.register_instruction(cil.CILArg)
        self.register_instruction(cil.CILCall, f'{node.new_type}_ctr')
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
        if source in self.globalvars[self.local_index:]:
            offset_src = self.context.lname[source]
            self.register_instruction(cil.CILDummy, f'lw $t0, {offset_src * -4}')
        else:
            offset_src = self.context.lname[source]
            self.register_instruction(cil.CILDummy, f'lw $a0, {offset_src * 4}')


        source = self.visit(node.expr)
        self.register_instruction(cil.CILAssign, self.context.lmap[node.identifier.name], source)
        return source

    @visitor.when(ast.Block)
    def visit(self, node: ast.Block):
        # print('Block')
        vinfo = 0
        for expr in node.expr_list:
            vinfo = self.visit(expr)
        return vinfo

    @visitor.when(ast.DynamicDispatch)
    def visit(self, node: ast.DynamicDispatch):
        # Save current frame pointer
        self.register_instruction(cil.CILDummy, 'sw $fp 0($sp)')
        
        # Generate code for each of the params and push them
        args = []
        for arg in reversed(node.arguments):
            vinfo = self.visit(arg)
            arg_node = self.register_instruction(cil.CILArg)
    
        instance = self.visit(node.instance)  # This is going to be param `self`
        self.register_instruction(cil.CILArg)

        # Here we have to compute the type, which is done using TYPEOF
        self.register_instruction(cil.CILTypeOf, instance)
        self.register_instruction(cil.CILVCall, None, node.method)

    @visitor.when(ast.StaticDispatch)
    def visit(self, node: ast.StaticDispatch):
        # Save current frame pointer
        self.register_instruction(cil.CILDummy, 'sw $fp 0($sp)')

        # Generate code for each of the params and push them
        args = []
        for arg in reversed(node.arguments):
            vinfo = self.visit(arg)
            arg_node = self.register_instruction(cil.CILArg)

        self.register_instruction(cil.CILVCall, node.dispatch_type, node.method)

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
        identifier = self.register_local(node.identifier)
        vinfo = self.visit(node.expression) if node.expression else default(
            node.ttype)

        self.register_instruction(cil.CILAssign, identifier.name, vinfo)
        return identifier

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
        vinfo = self.visit(node.expr)
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
        left_vinfo = self.visit(node.left)
        right_vinfo = self.visit(node.right)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILPlus, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Subtraction)
    def visit(self, node: ast.Subtraction):
        left_vinfo = self.visit(node.left)
        right_vinfo = self.visit(node.right)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILMinus, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Multiplication)
    def visit(self, node: ast.Multiplication):
        left_vinfo = self.visit(node.left)
        right_vinfo = self.visit(node.right)
        dest_vinfo = self.define_internal_local()
        self.register_instruction(cil.CILStar, dest_vinfo, left_vinfo,
                                  right_vinfo)
        return dest_vinfo

    @visitor.when(ast.Division)
    def visit(self, node: ast.Division):
        left_vinfo = self.visit(node.left)
        right_vinfo = self.visit(node.right)
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
