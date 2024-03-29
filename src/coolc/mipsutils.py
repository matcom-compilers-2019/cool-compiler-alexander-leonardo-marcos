#registers
class reg:

    zero = '$zero'
    a0 = '$a0'
    a1 = '$a1'
    a2 = '$a2'
    a3 = '$a3'

    v0 = '$v0'
    v1 = '$v1'

    s0 = '$s0'
    s1 = '$s1'
    s2 = '$s2'
    s3 = '$s3'
    s4 = '$s4'
    s5 = '$s5'
    s6 = '$s6'
    s7 = '$s7'

    t0 = '$t0'
    t1 = '$t1'
    t2 = '$t2'
    t3 = '$t3'
    t4 = '$t4'
    t5 = '$t5'
    t6 = '$t6'
    t7 = '$t7'
    t8 = '$t8'
    t9 = '$t9'

    gp = '$gp'
    sp = '$sp'
    fp = '$fp'
    ra = '$ra'

#operations
class op:

    la = 'la'
    lb = 'lb'
    lbu = 'lbu'
    ld = 'ld'
    lh = 'lh'
    lhu = 'lhu'
    lw = 'lw'
    lwcz = 'lwcz'
    lwl = 'lwl'
    lwr = 'lwr'
    sb = 'sb'
    sd = 'sd'
    sh = 'sh'
    sw = 'sw'
    swcz = 'swcz'
    swl = 'swl'
    swr = 'swr'
    ulh = 'ulh'
    ulhu = 'ulhu'
    ulw = 'ulw'
    ush = 'ush'
    usw = 'usw'

    abs = 'abs'
    add = 'add'
    addi = 'addi'
    addu = 'addu'
    addiu = 'addiu'
    and_bw = 'and'
    andi = 'andi'   
    div = 'div'
    divu = 'divu' 
    div = 'div'
    divu = 'divu'
    mul = 'mul'
    mulu = 'mulu'
    mulo = 'mulo'
    mulou = 'mulou'
    mult = 'mult'
    multu = 'multu'
    neg = 'neg'
    negu = 'negu'
    nor = 'nor'
    not_bw = 'not'
    or_bw = 'or'
    ori = 'ori'
    rem = 'rem'
    remu = 'remu'
    rol = 'rol'
    ror = 'ror'
    sll = 'sll'
    sllv = 'sllv'
    sra = 'sra'
    srav = 'srav'
    srl = 'srl'
    srlv = 'srlv'
    sub = 'sub'
    subu = 'subu'
    xor = 'xor'
    xori = 'xori'

    li = 'li'
    lid = 'li.d'
    lis = 'li.s'
    lui = 'lui'

    seq = 'seq'
    sge = 'sge'
    sgeu = 'sgeu'
    sgt = 'sgt'
    sgtu = 'sgtu'
    sle = 'sle'
    sleu = 'sleu'
    slt = 'slt'
    slti = 'slti'
    sltu = 'sltu'
    sltiu = 'sltiu'
    sne = 'sne'

    b = 'b'
    bczt = 'bczt'
    bczf = 'bczf'
    beq = 'beq'
    beqz = 'beqz'
    bge = 'bge'
    bgeu = 'bgeu'
    bgez = 'bgez'
    bgezal = 'bgezal'
    bgt = 'bgt'
    bgtu = 'bgtu'
    bgtz = 'bgtz'
    ble = 'ble'
    bleu = 'bleu'
    blez = 'blez'
    bgezal = 'bgezal'

    bltzal = 'bltzal'
    blt = 'blt'
    bltu = 'bltu'
    bltz = 'bltz'
    bne = 'bne'
    bnez = 'bnez'
    j = 'j'
    jal = 'jal'
    jalr = 'jalr'
    jr = 'jr'

    move = 'move'
    mfhi = 'mfhi'
    mflo = 'mflo'
    mthi = 'mthi'
    mtlo = 'mtlo'
    mfcz = 'mfcz'
    mfc1d = 'mfc1.d'
    mtcz = 'mtcz'

    rfe = 'rfe'
    syscall = 'syscall'
    brk = 'break'
    nop = 'nop'

#types
class datatype:
    align = '.align'
    ascii = '.ascii'
    asciiz = '.asciiz'
    byte = '.byte'
    double = '.double'
    floatt = '.float'
    half = '.half'
    space = '.space'
    word = '.word'
    