from . import cilast as ast
from . import visitor
from .scope import VariableInfo
from .mipsutils import datatype, op, reg


class Cil2MipsVisitor:
    def __init__(self, context):
        self.dotdata = []
        self.dotcode = []
        self.context = context

    # ======================================================================
    # =[ UTILS ]============================================================
    # ======================================================================
    
    def init_str_funcs(self):
        self.init_str_length()
        self.init_str_concat()
        self.init_str_substr()

    def init_str_concat(self):
        self.emit_label('String_concat')
        self.emit_code(f'move $fp, $sp')

        self.visit(ast.CILAllocate(None, 'Int'))		# Create new Int object
        self.emit_code('move $v1 $v0')												# Save new Int Object

        self.visit(ast.CILAllocate(None, 'String'))		# Create new String object
        self.emit_code('move $t3 $v0')			# Store new String object

        self.emit_code('lw $a1 12($fp)')		# Self
        self.emit_code('lw $a2 16($fp)')		# Boxed String to concat

        self.emit_code('lw $t1 12($a1)')		# Self's length Int object
        self.emit_code('lw $t1 12($t1)')		# Self's length

        self.emit_code('lw $t2 12($a2)')		# strings to concat's length Int object
        self.emit_code('lw $t2 12($t2)')		# strings to concat's length

        self.emit_code('addu $t0 $t2 $t1') 		# New string's length
        self.emit_code('sw $t0 12($v1)')			# Store new string's length into box

        self.emit_code('lw $a1 16($a1)')		# Unbox strings
        self.emit_code('lw $a2 16($a2)')

        self.emit_code('addi $t0 $t0 1')		# Add space for \0
        self.allocate_memory('$t0', register=True)	# Allocate memory for new string
        self.emit_code('move $t5 $v0')					# Keep the string's reference in v0 and use t7

        self.emit_code('move $t4 $a1')			# Index for iterating the self string
        self.emit_code('addu $a1 $a1 $t1')		# self's copy limit
        self.emit_label('_strcat_copy_')
        self.emit_code('beq $t4 $a1 _end_strcat_copy_')	# No more characters to copy

        self.emit_code('lb $a0 0($t4)')			# Copy the character
        self.emit_code('sb $a0 0($t5)')

        self.emit_code('addi $t5 $t5 1')		# Advance indices
        self.emit_code('addi $t4 $t4 1')
        self.emit_code('j _strcat_copy_')
        self.emit_label('_end_strcat_copy_')

        # Copy 2nd string

        self.emit_code('move $t4 $a2')			# Index for iterating the strings
        self.emit_code('addu $a2 $a2 $t2')		# self's copy limit
        self.emit_label('_strcat_copy_snd_')
        self.emit_code('beq $t4 $a2 _end_strcat_copy_snd_')	# No more characters to copy

        self.emit_code('lb $a0 0($t4)')			# Copy the character
        self.emit_code('sb $a0 0($t5)')

        self.emit_code('addi $t5 $t5 1')		# Advance indices
        self.emit_code('addi $t4 $t4 1')
        self.emit_code('j _strcat_copy_snd_')
        self.emit_label('_end_strcat_copy_snd_')

        self.emit_code('sb $0 0($t5)')			# End string with \0


        self.emit_code('sw $v1 12($t3)')		# New length
        self.emit_code('sw $v0 16($t3)')		# New string

        self.emit_code('move $v0 $t3')			# Return new String object in $v0
        self.emit_code('jr $ra')
        self.emit_code('')


    def init_str_substr(self):
        self.emit_label('String_substr')        
        self.emit_instruction(op.move, reg.fp, reg.sp)
        self.emit_instruction(op.lw, reg.t5, self.off_reg(0, reg.fp, 12))
        self.emit_instruction(op.lw, reg.a1, self.off_reg(1, reg.fp, 12))
        self.emit_instruction(op.lw, reg.a1, self.off_reg(0, reg.a1, 12))
        self.emit_instruction(op.lw, reg.a2, self.off_reg(2, reg.fp, 12))
        self.emit_instruction(op.lw, reg.a2, self.off_reg(0, reg.a2, 12))
        self.emit_instruction(op.blt, reg.a1, '$0', '_index_negative')
        self.emit_instruction(op.blt, reg.a2, '$0', '_index_negative')
        self.emit_instruction(op.add, reg.a2, reg.a1, reg.a2)
        self.emit_instruction(op.lw, reg.a3, self.off_reg(0, reg.t5, 12))
        self.emit_instruction(op.lw, reg.a3, self.off_reg(0, reg.a3, 12))
        self.emit_instruction(op.bgt, reg.a2, reg.a3, '_index_out')


        self.visit(ast.CILAllocate, None, 'String')
        self.emit_instruction(op.move, reg.v1, reg.a0)

        self.visit(ast.CILAllocate, None, 'Int')
        self.emit_instruction(op.move, reg.t0, reg.a0)
        self.emit_instruction(op.sw, reg.a2, self.off_reg(0, reg.t0, 12))
        self.allocate_memory('$a2', register=True)	# $v0 -> address of the string

        self.emit_instruction(op.sw, reg.t0, self.off_reg(0, reg.v1, 12))
        self.emit_instruction(op.sw, reg.v0, self.off_reg(1, reg.v1, 12))

        self.emit_instruction(op.move, reg.t1, reg.v0)
        
        self.emit_instruction(op.lw, reg.t5, self.off_reg(1, reg.t5, 12))
        self.emit_instruction(op.move, reg.t4, reg.t5)
        self.emit_instruction(op.addu, reg.t4, reg.t4, reg.a1)
        self.emit_instruction(op.addu, reg.t5, reg.t5, reg.a2)

        self.emit_label('_substr_copy')
        self.emit_instruction(op.bge, reg.t4, reg.t5, '_end_substr_copy')
        self.emit_instruction(op.lb, reg.a0, self.off_reg(0, reg.t4))
        self.emit_instruction(op.sb, reg.a0, self.off_reg(0, reg.t1))

        self.emit_instruction(op.addi, reg.t1, reg.t1, 1)
        self.emit_instruction(op.addi, reg.t4, reg.t4, 1)
        self.emit_instruction(op.j, '_substr_copy')

        self.emit_label('_index_negative')
        self.emit_instruction(op.la, reg.a0, '_index_negative_msg')
        self.emit_instruction(op.b, '_subst_abort')

        self.emit_label('_index_out')
        self.emit_instruction(op.la, reg.a0, '_index_out_msg')
        self.emit_instruction(op.b, '_subst_abort')

        self.emit_label('_subst_abort')
        self.emit_instruction(op.li, reg.v0, 4)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.la, reg.a0, '_abort_msg')
        self.emit_instruction(op.li, reg.v0, 4)        
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.li, reg.v0, 10)
        self.emit_instruction(op.syscall)

        self.emit_label('_end_substr_copy')
        self.emit_instruction(op.move, reg.a0, reg.v1)
        self.emit_instruction(op.jr, reg.ra)


    def init_str_length(self):
        self.emit_label('String_length')
        self.emit_instruction(op.lw, reg.a0, self.off_reg(1, reg.sp))
        self.emit_instruction(op.li, reg.a1, 0)
        self.emit_label('length_main_loop')
        self.emit_instruction(op.lb, reg.t1, self.off_reg(0, reg.a0))
        self.emit_instruction(op.beqz, reg.t1, 'length_end')
        self.emit_instruction(op.addi, reg.a0, reg.a0, 1)
        self.emit_instruction(op.addi, reg.a1, reg.a1, 1)
        self.emit_instruction(op.j, 'length_main_loop')
        self.emit_label('length_end')
        self.emit_instruction(op.move, reg.a0, reg.a1)
        self.emit_instruction(op.jr, reg.ra)

    def init_obj_funcs(self):
        self.init_obj_abort()
        self.init_obj_typename()
        self.init_obj_copy()

    def init_obj_abort(self):
        self.emit_label('Object_abort')
        self.emit_instruction(op.li, reg.v0, 10)
        self.emit_instruction(op.syscall)

    def init_obj_typename(self):
        self.emit_label('Object_type_name')
        self.emit_instruction(op.move, reg.fp, reg.sp)
        self.visit(ast.CILAllocate(None, 'String'))
        self.emit_instruction(op.move, reg.v1, reg.v0)
        self.visit(ast.CILAllocate(None, 'Int'))
        self.emit_instruction(op.lw, reg.a1, self.off_reg(3, reg.fp))
        self.emit_instruction(op.lw, reg.a1, self.off_reg(0, reg.a1))
        self.emit_instruction(op.mul, reg.a1, reg.a1, 4)
        self.emit_instruction(op.addu, reg.a1, reg.a1, reg.s1)
        self.emit_instruction(op.lw, reg.a1, self.off_reg(0, reg.a1))
        self.emit_instruction(op.move, reg.a2, '$0')
        self.emit_instruction(op.move, reg.t2, reg.a1)
        self.emit_label('_str_len_clsname')
        self.emit_instruction(op.lb, reg.a0, self.off_reg(0, reg.t2))
        self.emit_instruction(op.beq, reg.a0, '$0', '_end_clsname_len')
        self.emit_instruction(op.addu, reg.a2, reg.a2, 1)
        self.emit_instruction(op.addu, reg.t2, reg.t2, 1)
        self.emit_instruction(op.j, '_str_len_clsname')
        self.emit_label('_end_clsname_len')
        self.emit_instruction(op.sw, reg.a2, self.off_reg(3, reg.v0))
        self.emit_instruction(op.sw, reg.v0, self.off_reg(3, reg.v1))
        self.emit_instruction(op.sw, reg.a1, self.off_reg(4, reg.v1))
        self.emit_instruction(op.move, reg.v0, reg.v1)
        self.emit_instruction(op.jr, reg.ra)



    def init_obj_copy(self):		
        self.emit_label('Object_copy')
        self.emit_instruction(op.move, reg.fp, reg.sp)
        self.emit_instruction(op.lw, reg.t0, self.off_reg(0, reg.fp, 12))
        self.emit_instruction(op.lw, reg.a0, self.off_reg(1, reg.t0))
        self.emit_instruction(op.move, reg.t4, reg.a0)
        self.emit_instruction(op.li, reg.v0, 9)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.move, reg.t2, reg.v0)
        self.emit_instruction(op.li, reg.t2, 0)
        self.emit_label('Object_copy_loop')
        self.emit_instruction(op.lw, reg.t1, self.off_reg(0, reg.t0))
        self.emit_instruction(op.sw, reg.t1, self.off_reg(0, reg.v0))
        self.emit_instruction(op.addi, reg.t0, reg.t0, 4)
        self.emit_instruction(op.addi, reg.v0, reg.v0, 4)
        self.emit_instruction(op.addi, reg.t3, reg.t3, 4)
        self.emit_instruction(op.ble, reg.t4, reg.t3, 'Object_copy_loop')
        self.emit_label('Object_copy_end')
        self.emit_instruction(op.move, reg.v0, reg.t2)
        self.emit_instruction(op.jr, reg.ra)


    def init_io_funcs(self):
        self.init_io_in_int()
        self.init_io_in_str()
        self.init_io_out_int()
        self.init_io_out_str()

    def init_io_in_int(self):
        self.emit_label('IO_in_int')
        self.emit_instruction(op.li, reg.v0, 5)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.move, reg.a0, reg.v0)
        self.emit_instruction(op.jr, reg.ra)

    def init_io_in_str(self):
        self.emit_label('IO_in_string')
        self.emit_instruction(op.li, reg.a1, 1024)
        self.emit_instruction(op.li, reg.v0, 8)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.jr, reg.ra)

    def init_io_out_int(self):
        self.emit_label('IO_out_int')
        self.emit_instruction(op.lw, reg.a0, self.off_reg(1, reg.sp))
        self.emit_instruction(op.li, reg.v0, 1)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.jr, reg.ra)

    def init_io_out_str(self):
        self.emit_label('IO_out_string')
        self.emit_instruction(op.lw, reg.a0, self.off_reg(1, reg.fp, 12))
        self.emit_instruction(op.lw, reg.a0, self.off_reg(1, reg.a0))
        self.emit_instruction(op.li, reg.v0, 4)
        self.emit_instruction(op.syscall)
        self.emit_instruction(op.jr, reg.ra)

    def init_def_obj_func(self):
        self.init_obj_funcs()
        self.init_io_funcs()
        self.init_str_funcs()

    def init_utils(self):
        self.dotdata.append('.data')
        self.dotcode.append('.text')

    def allocate_memory(self, size=None, register=False):
        if register:
            self.emit_instruction(op.move, reg.a0, size)
        else:
            if size:
                self.emit_instruction(op.li, reg.a0, size)                
        self.emit_instruction(op.li, reg.v0, 9)                
        self.emit_instruction(op.syscall)                

    def pusha(self, excep = []):
        dic = reg.__dict__
        for key in dic.keys():
            if not str(key).startswith('_') and not excep.__contains__(key):
                self.push(dic[key])

    def popa(self, excep = []):
        dic = reg.__dict__
        keys = list(dic.keys())
        keys = list(reversed(keys))
        for key in keys:
            if not str(key).startswith('_') and not excep.__contains__(key):
                self.pop(dic[key])

    def emit_data_rec(self, ttype, data, label = None):
        datas = ', '.join(map(lambda x: str(x), data))
        to_emit = f'{ttype} {datas}'
        if label:
            to_emit = label + ': ' + to_emit
        self.emit_data(to_emit)

    def emit_code(self, msg):
        self.dotcode.append(msg)

    def emit_data(self, msg):
        self.dotdata.append(msg)

    def off_reg(self, off, register, delta=0):
        offset = int(off) * 4 + delta
        return f'{offset}({register})'

    def push(self, register, off = 0):
        self.emit_instruction(op.sw, register, self.off_reg(off, reg.sp))
        self.emit_instruction(op.addi, reg.sp, reg.sp, -4)
        # self.emit_code(f'sw {reg} {off * 4}($sp)')
        # self.emit_code(f'addi $sp $sp -4')

    def pop(self, register):
        self.emit_instruction(op.lw, register, self.off_reg(4, reg.sp))
        self.stack_allign()
        # self.emit_code(f'lw {reg} 4($sp)')
        # self.emit_code(f'addi $sp $sp 4')

    def stack_allign(self):
        self.emit_instruction(op.addi, reg.sp, reg.sp, 4)
        # self.emit_code('addi $sp $sp 4')

    def emit_label(self, label):
        self.emit_code(label + ':')

    def eval_infix_func(self, node):
        self.visit(node.left)
        self.push(reg.a0)
        self.visit(node.right)
        self.pop(reg.t1)

    def infix_func(self, node, op, dest = reg.a0, source1 = reg.t1, source2 = reg.a0):
        self.eval_infix_func(node)
        self.emit_code(f'{op} {dest} {source1} {source2}')

    def __emit_i__(self, inst, args):
        result = inst
        if len(args) > 0:
            result += ' '
            params = filter(lambda x: x != None, args)
            result += ', '.join(map(lambda x: str(x), params))
        self.emit_code(result)

    def emit_instruction(self, inst: op, arg1: reg = None, arg2: reg = None, arg3: reg = None):
        self.__emit_i__(inst, [arg1, arg2, arg3])

    # ======================================================================
    # =[ VISIT ]============================================================
    # ======================================================================

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.CILProgram)
    def visit(self, node: ast.CILProgram):
        self.emit_code("\n# Program")
        # Init some utility functions
        self.init_utils()

        # Visit every data node in Program
        # self.emit_code("\n# .data:")
        # print(node.dotdata)
        for datanode in node.dotdata:
            self.visit(datanode)

        # Error mensages
        self.emit_data('_index_negative_msg: .asciiz \"Index to substr is negative\\n\"')
        self.emit_data('_index_out_msg: .asciiz \"Index out range exception\\n\"')
        self.emit_data('_abort_msg: .asciiz \"Execution aborted\\n\"')
        self.emit_data('_div_zero_msg: .asciiz \"Division by zero exception\\n\"')

        # self.emit_code("\n# .types:")
        # print(node.dottypes)
        # Visit every type node in Program
        for typenode in node.dottypes:
            self.visit(typenode)

        # self.emit_code("\n# .code:")
        # print(node.dotcode)
        # Visit every code node in Program

        mips_funcs = [
            'IO_in_int',
            'IO_in_string',
            'IO_out_int',
            'IO_out_string',
            'String_length',
            'String_concat',
            'String_substr',
        ]
        for codenode in node.dotcode:
            if codenode.fname not in mips_funcs:
                self.visit(codenode)
        
        self.init_def_obj_func()

    @visitor.when(ast.CILType)
    def visit(self, node: ast.CILType):
        """
        Object layout:
        - Class Tag
        - Object Size
        - Parent ptr
        - Function 1
        - Function 2
        ...
        """
        # self.emit_code("\n# Type")
        self.emit_data(f'{node.name}: .word {self.context.tags[node.name]}')
        # self.emit_data_rec(datatype.word, [self.context.tags[node.name]], label=node.name)
        # Generate virtual table for this type
        # print(node.name)
        # print(node.methods)
        for method in node.methods:
            # self.visit(method)
            name = '_'.join(method.mname.split('_')[1:])
            # print(method.mname, name)
            self.emit_data(f'{node.name}_{name}_method: .word {self.context.mmap[method.mname]}')

            # self.emit_data(f'   .word {self.context.mmap[method.mname]}')
            # self.emit_data_rec(datatype.word, self.context.mmap[method.mname])

    @visitor.when(ast.CILData)
    def visit(self, node: ast.CILData):
        print(node.value)

        if node.value == '':
            value = '""'
        elif isinstance(node.value, str):
            value = node.value
        else:
            value = f'"{node.value}"'
        self.emit_data(f'{node.name}: .asciiz {value}')
        # self.emit_data_rec(datatype.asciiz, [node.value], node.name)

    @visitor.when(ast.CILFunction)
    def visit(self, node: ast.CILFunction):
        # print("Function")
        # print(node.fname + " Function")
        methods = [
            'Object_abort',
            'Object_type_name',
            'Object_copy',
            'String_concat',
            'String_substr',
            'String_length',
            'IO_in_int',
            'IO_out_int',
            'IO_in_string',
            'IO_out_string',
        ]
        if node.fname in methods: 
            return

        self.emit_code("\n# Function start")
        self.emit_label(node.fname)
        self.emit_instruction(op.move, reg.fp, reg.sp)
        self.push(reg.ra)

        # self.pusha(['a0'])

        for instruction in node.instructions:
            self.visit(instruction)

        # self.popa(['a0'])
        computed = self.off_reg(1, reg.sp)
        self.emit_instruction(op.lw, reg.ra, computed)

        z = 4 * node.param_count + 8
        self.emit_instruction(op.addi, reg.sp, reg.sp, z)
        
        computed = self.off_reg(0, reg.sp)
        self.emit_instruction(op.lw, reg.fp, computed)
        self.emit_instruction(op.jr, reg.ra)
        self.emit_code("\n# Function end")

    @visitor.when(ast.CILMethod)
    def visit(self, node: ast.CILMethod):
        self.emit_code("\n# Method")        
        # print('AAAAAAAAA')
        name = '_'.join(node.mname.split('_')[1:])
        self.emit_data(f'{self.current_class_name}_{name}: .word {self.context.mmap[node.mname]}')

    @visitor.when(ast.CILDummy)
    def visit(self, node: ast.CILDummy):
        self.emit_code("\n# Dummy")
        self.emit_code(node.value)

    # @visitor.when(ast.CILParam)
    # def visit(self, node: ast.CILParam):
    # 	pass

    @visitor.when(ast.CILLocal)
    def visit(self, node: ast.CILLocal):
        self.push(reg.t0)

    @visitor.when(ast.CILAssign)
    def visit(self, node: ast.CILAssign):
        self.emit_code("\n# Assign")
        # print(list(self.context.lmap.keys()))
        dest = self.context.lmap[node.dest.name]
        dest_offset = self.off_reg(-dest, reg.sp)
        self.emit_instruction(op.sw, reg.a0, dest_offset)

        # self.emit_code(f'move {dest} {node.source}')

    @visitor.when(ast.CILPlus)
    def visit(self, node: ast.CILPlus):
        self.emit_code("\n# Plus")
        self.infix_func(node, op.add)
        
    @visitor.when(ast.CILMinus)
    def visit(self, node: ast.CILMinus):
        self.emit_code("\n# Minus")
        self.infix_func(node, op.sub)

    @visitor.when(ast.CILStar)
    def visit(self, node: ast.CILStar):
        self.emit_code("\n# Star")
        self.infix_func(node, op.mul)

    @visitor.when(ast.CILDiv)
    def visit(self, node: ast.CILDiv):
        self.emit_code("\n# Div")
        self.infix_func(node, op.div)

    @visitor.when(ast.CILEqual)
    def visit(self, node: ast.CILEqual):
        self.emit_code("\n# Equal")
        self.eval_infix_func(node)
        return op.beq

    @visitor.when(ast.CILLessThan)
    def visit(self, node: ast.CILLessThan):
        self.emit_code("\n# LessThan")
        self.eval_infix_func(node)
        return op.blt

    @visitor.when(ast.CILLessThanOrEqual)
    def visit(self, node: ast.CILLessThanOrEqual):
        self.emit_code("\n# LessThanOrEqual")
        self.eval_infix_func(node)
        return op.ble

    @visitor.when(ast.CILGoto)
    def visit(self, node: ast.CILGoto):
        self.emit_code("\n# Goto")
        self.emit_instruction(op.j, node.name)

    @visitor.when(ast.CILGotoIf)
    def visit(self, node: ast.CILGotoIf):
        self.emit_code("\n# GotoIf")
        branch_instruction = self.visit(node.condition)
        self.emit_instruction(branch_instruction, reg.a0, reg.t1, node.label)

    @visitor.when(ast.CILGetAttrib)
    def visit(self, node: ast.CILGetAttrib):
        self.emit_code("\n# GetAttrib")
        # Attribute offset
        # loff = self.context.lmap[node.attribute]
        
        # $a0 contains the type of the instance.
        # Here we compute in $a0 the offset of the attribute
        computed = self.off_reg(node.attribute, reg.a0)
        
        # Load into $a0 the value of the attribute
        self.emit_instruction(op.lw, reg.a0, computed)

    @visitor.when(ast.CILSetAttrib)
    def visit(self, node: ast.CILSetAttrib):
        self.emit_code("\n# SetAttrib")

        # This is a local variable, so load the contents
        # print(node.instance.name, node.instance.holder)
        instance_offset = self.off_reg(node.instance.holder, reg.fp)
        self.emit_instruction(op.lw, reg.a1, instance_offset)

        # Depending on what the node is, load it
        if isinstance(node.src, int):
            self.emit_instruction(op.li, reg.a0, node.src)
        elif isinstance(node.src, ast.CILData):
        # elif node.src.name[:5] == "data_":
            self.emit_instruction(op.la, reg.a0, node.src.name)
        elif node.src == 'void':
            self.emit_instruction(op.li, reg.a0, 0)
        elif isinstance(node.src, str):
            src_offset = self.off_reg(self.context.lmap[node.src], reg.fp)
            self.emit_instruction(op.lw, reg.a0, src_offset)
        else:
            src_offset = self.off_reg(self.context.lmap[node.src.name], reg.fp)
            self.emit_instruction(op.lw, reg.a0, src_offset)

        # Store the value
        # print(node)
        if isinstance(node.attribute, int):
            attr = node.attribute
        else:
            print(node.attribute.name)
            print(node.attribute.holder)
            attr = node.attribute.holder
        attr_offset = self.off_reg(node.attribute, reg.a1, 12)
        # attr_offset = self.off_reg(self.context.amap[node.attribute], reg.a1, 12)
        self.emit_instruction(op.sw, reg.a0, attr_offset)

    @visitor.when(ast.CILAllocate)
    def visit(self, node: ast.CILAllocate):
        self.emit_code("\n# Allocate")
        if node.ttype == "void":
            self.emit_code(f'la $a0 void')
        else:
            tag = self.context.tags[node.ttype] * 4  # Why not 8
            self.emit_instruction(op.lw, reg.a0, self.off_reg(tag, reg.s0))
            self.push(reg.a0)
            if node.dest:
                self.visit(ast.CILCall(node.dest.holder, "Object_copy"))
            else:
                self.visit(ast.CILCall(None, "Object_copy"))

    @visitor.when(ast.CILTypeOf)
    def visit(self, node: ast.CILTypeOf):
        self.emit_code("\n# TypeOf")
        self.emit_instruction(op.lw, reg.a1, self.off_reg(node.var.holder, reg.fp))
        self.emit_instruction(op.lw, reg.a0, self.off_reg(0, reg.a1))
        self.emit_instruction(op.sw, reg.a0, self.off_reg(node.dest.holder, reg.fp))

    @visitor.when(ast.CILLabel)
    def visit(self, node: ast.CILLabel):
        self.emit_label(node.name)

    @visitor.when(ast.CILCall)
    def visit(self, node: ast.CILCall):
        self.emit_code("\n# Call")
        self.emit_instruction(op.jal, node.func)

    @visitor.when(ast.CILVCall)
    def visit(self, node: ast.CILVCall):
        self.emit_code("\n# VCall")

        # # Save return address and frame pointer
        # self.emit_code(f'addi $sp, $sp, -8')
        # self.emit_code(f'sw $ra, 4($sp)')
        # self.emit_code(f'sw $fp, 8($sp)')

        # if isinstance(node.ttype, VariableInfo):
        #     # If node.type is a local CIL variable
        #     # print(node.ttype.name)
        #     # print(node.ttype.holder)
        #     self.emit_instruction(op.lw, reg.a2, self.off_reg(node.ttype.holder, reg.fp))
        # else:
        #     # If node.type a type name
        #     # print(node.ttype)
        #     self.emit_code(f'li $a2, {node.ttype}')
        # self.emit_code(f'mulu $a2, $a2, 4')
        # self.emit_code(f'addu $a2, $a2, $s0')
        # self.emit_code(f'lw $a1, 0($a2)')

        # print(node.func)
        # print(node.func.holder)
        # if isinstance(node.func, str):
        #     self.emit_instruction(op.lw, reg.a0, self.off_reg(self.context.mmap[node.func], reg.a2))            
        # else:
        #     self.emit_instruction(op.lw, reg.a0, self.off_reg(node.func.holder, reg.a2))
        # print(self.context.fmap)
        # print(node.func.holder)
        self.emit_instruction(op.lw, reg.a0, self.off_reg(self.context.fmap[node.func], reg.a2))            

        # Call the function at 0($a0)
        
        # print(node.func)
        # print(self.context.mmap.items())
        # print(self.context.fmap.items())
        # print(self.context.mmap[node.func])
        # self.emit_code(f'jal {node.func}')
        self.emit_code(f'jalr $a0')

        # Restore return address and frame pointer
        self.emit_code(f'lw $fp, 8($sp)')
        self.emit_code(f'lw $ra, 4($sp)')
        self.emit_code(f'addi $sp, $sp, 8')

        # Save value after restoring $fp
        self.emit_instruction(op.sw, reg.a0, self.off_reg(node.dest.holder, reg.fp))

        # # Check prototypes table for the dynamic type
        # if node.ttype[0] != '_':
        # 	self.emit_code(f'li $a2, {self.type_index.index(node.ttype)}')
        # else:
        # 	self.emit_code(f'lw $a2, {self.offset[node.ttype]}($fp)')



    @visitor.when(ast.CILArg)
    def visit(self, node: ast.CILArg):
        self.emit_code("\n# Arg")
        self.push(reg.a0)

    @visitor.when(ast.CILReturn)
    def visit(self, node: ast.CILReturn):
        self.emit_code("\n# Return")
        if isinstance(node.value, int):
            self.emit_instruction(op.li, reg.a0, node.value)
        elif isinstance(node.value, ast.CILLocal):
            computed = self.off_reg(node.value.vinfo.holder, reg.fp)
            self.emit_instruction(op.lw, reg.a0, computed)
        elif node.value == None:
            pass
        else:
            computed = self.off_reg(node.value.holder, reg.fp)
            self.emit_instruction(op.lw, reg.a0, computed)

    # @visitor.when(ast.CILLoad)
    # def visit(self, node: ast.CILLoad):
    # 	self.emit_instruction(op.li, reg.a0, node.value)

    @visitor.when(ast.CILLength)
    def visit(self, node: ast.CILLength):
        pass

    @visitor.when(ast.CILConcat)
    def visit(self, node: ast.CILConcat):
        pass

    @visitor.when(ast.CILPrefix)
    def visit(self, node: ast.CILPrefix):
        pass

    @visitor.when(ast.CILSubstring)
    def visit(self, node: ast.CILSubstring):
        pass
