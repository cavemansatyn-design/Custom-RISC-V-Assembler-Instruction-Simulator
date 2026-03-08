import sys
inputf, outputf = sys.argv[1], sys.argv[2]
instructions = []
instru=[]
with open(inputf,"r") as tf:
    instru = tf.readlines()
pc = 0

with open(outputf, "w") as f:
    f.write("")
    
for i,j in enumerate(instru):
    instructions.append(j.strip())
    

reg = {}
for i in range(32):
    address = format(i, '032b')  # 32 bit binary string without 0b
    reg[address] = format(0, '032b')
reg[format(2, '032b')] = format(380, '032b')

memory = {
    "0x00010000": "0b00000000000000000000000000000000",
    "0x00010004": "0b00000000000000000000000000000000",
    "0x00010008": "0b00000000000000000000000000000000",
    "0x0001000C": "0b00000000000000000000000000000000",
    "0x00010010": "0b00000000000000000000000000000000",
    "0x00010014": "0b00000000000000000000000000000000",
    "0x00010018": "0b00000000000000000000000000000000",
    "0x0001001C": "0b00000000000000000000000000000000",
    "0x00010020": "0b00000000000000000000000000000000",
    "0x00010024": "0b00000000000000000000000000000000",
    "0x00010028": "0b00000000000000000000000000000000",
    "0x0001002C": "0b00000000000000000000000000000000",
    "0x00010030": "0b00000000000000000000000000000000",
    "0x00010034": "0b00000000000000000000000000000000",
    "0x00010038": "0b00000000000000000000000000000000",
    "0x0001003C": "0b00000000000000000000000000000000",
    "0x00010040": "0b00000000000000000000000000000000",
    "0x00010044": "0b00000000000000000000000000000000",
    "0x00010048": "0b00000000000000000000000000000000",
    "0x0001004C": "0b00000000000000000000000000000000",
    "0x00010050": "0b00000000000000000000000000000000",
    "0x00010054": "0b00000000000000000000000000000000",
    "0x00010058": "0b00000000000000000000000000000000",
    "0x0001005C": "0b00000000000000000000000000000000",
    "0x00010060": "0b00000000000000000000000000000000",
    "0x00010064": "0b00000000000000000000000000000000",
    "0x00010068": "0b00000000000000000000000000000000",
    "0x0001006C": "0b00000000000000000000000000000000",
    "0x00010070": "0b00000000000000000000000000000000",
    "0x00010074": "0b00000000000000000000000000000000",
    "0x00010078": "0b00000000000000000000000000000000",
    "0x0001007C": "0b00000000000000000000000000000000"
}
mem_keys = [
    "0x00010000", "0x00010004", "0x00010008", "0x0001000C",
    "0x00010010", "0x00010014", "0x00010018", "0x0001001C",
    "0x00010020", "0x00010024", "0x00010028", "0x0001002C",
    "0x00010030", "0x00010034", "0x00010038", "0x0001003C",
    "0x00010040", "0x00010044", "0x00010048", "0x0001004C",
    "0x00010050", "0x00010054", "0x00010058", "0x0001005C",
    "0x00010060", "0x00010064", "0x00010068", "0x0001006C",
    "0x00010070", "0x00010074", "0x00010078", "0x0001007C"
]
def sign_ext(binary_stri, bit_len, output_bits):
    #string to binary and extend to desired 
    num = int(binary_stri, 2)  # convt to int
    if binary_stri[0] =='1':  # check negative
        num -=(1 << bit_len)  #two's compliment adjust
    return format(num & ((1<< output_bits) -1), f'0{output_bits}b')  # sign ext
    
def imm_conver(num, length): #num and length are base 10 and an integer 
    return bin(num & ((1 << length) - 1))[2:].zfill(length) #returns binary of num of specified length without 0b and it is a string
    
def bin_to_sign(val):
    num=int(val,2) #converrts val which is a binary and base is 2 as it is written to integer
    return num-(1<<32) if val[0]=="1" else num # it returns int
#there is no "0b" here in returning value neither in input value

def sing_to_bin(val):
    return bin(val&((1<<32)-1))[2:].zfill(32) # it returns string
#there is no "0b" here in returning value neither in input value





def R_type(instr):
    global pc, reg
    

    funct7 = instr[:7]
    rs2 = instr[7:12]
    rs1 = instr[12:17]
    funct3 = instr[17:20]
    rd = instr[20:25]
    opcode = instr[25:]
    
    rs1_ind = int(rs1, 2)
    rs2_ind = int(rs2, 2)
    rd_ind = int(rd, 2)
    
    val1 = reg[format(rs1_ind, '032b')]
    val2 = reg[format(rs2_ind, '032b')]
    

    val1_sign = bin_to_sign(val1)
    val2_sign = bin_to_sign(val2)
    
    result = None
    
   
    if funct3 == "000":
        if funct7 == "0000000":  # ADD
            result = sing_to_bin(val1_sign + val2_sign)
        elif funct7 == "0100000":  
            result = sing_to_bin(val1_sign - val2_sign)
        else:
            print("funct7 not valid for funct3=000 and an Rtype")
            sys.exit()
    
    elif funct3 == "010":  # SLT 
        result = format(1, '032b') if val1_sign < val2_sign else format(0, '032b')
        
    
    elif funct3 == "101" and funct7 == "0000000":  # SRL
        shift_amount = int(val2, 2) & 0x1F 
        result = format(int(val1, 2) >> shift_amount, '032b')
    
    elif funct3 == "111":  # AND
        result = format(int(val1, 2) & int(val2, 2), '032b')
    
    elif funct3 == "110":  # OR
        result = format(int(val1, 2) | int(val2, 2), '032b')
    else:
        print("funct3 not valid for Rtype")
        sys.exit()
    
   
    if result is not None:
        reg[format(rd_ind, '032b')] = result
    
  
    pc = sing_to_bin(bin_to_sign(pc) + 4)

def S_type(instr):
    global pc, reg, memory
    opcode = instr[-7:] 
    imm = instr[0:7] + instr[-12:-7]  
    func3 = instr[-15:-12]  
    rs1 = instr[-20:-15] 
    rs2 = instr[-25:-20] 
    if(func3 != "010"):
        print("Invalid func3 for S-type")
        sys.exit()
    rs1 = int(rs1, 2)
    rs2 = int(rs2, 2)
    imm = bin_to_sign(imm.zfill(32)) 

    mem_address = f"0x{bin_to_sign(reg[format(rs1, '032b')])+ imm:08X}"
    memory[mem_address] = "0b" + reg[format(rs2, '032b')]
    pc = sing_to_bin(bin_to_sign(pc) + 4)


    
def I_type(instr):
    global pc, reg

    opcode = instr[25:]
    rd = format(int(instr[20:25], 2), '032b')
    funct3 = instr[17:20]
    rs1 = format(int(instr[12:17], 2), '032b')
    imm = instr[:12]
    imm = sign_ext(imm, 12, 32)
    imm = bin_to_sign(imm)


    val1 = bin_to_sign(reg[rs1])
    if opcode == "0000011":
        if(funct3 != "010"):
            print("Invalid funct3 for I-type")
            sys.exit()
        mem_address = "0x" + format(val1 + imm, '08X').upper()
        reg[rd] = memory.get(mem_address, "0b00000000000000000000000000000000")[2:]

    elif opcode == "0010011":
        if funct3 == "000":
            result = sing_to_bin(val1 + imm)
            reg[rd] = result
        else:
            print("Invalid funct3 for I-type")
            sys.exit()

    elif opcode == "1100111":
        if(funct3 != "000"):
            print("Invalid funct3 for I-type")
            sys.exit()
            
        reg[rd] = sing_to_bin(bin_to_sign(pc) + 4)

        final_ans = sing_to_bin(val1 + imm)
        final_ans = final_ans[:31] + '0'  

        pc = sing_to_bin(bin_to_sign(final_ans))

        reg[format(0, '032b')] = "00000000000000000000000000000000"
        return  

    pc = sing_to_bin(bin_to_sign(pc) + 4)


def B_type(instr):
    global pc
    imm = instr[0] + instr[24] + instr[1:7] + instr[20:24] + "0"
    rs1=instr[12:17]
    rs2=instr[7:12]
    f3=instr[17:20]
    rs1 = bin_to_sign(rs1)
    rs2 = bin_to_sign(rs2)
    imm =sign_ext(imm, 13, 32)


    if f3=="000" :
        if reg[format(rs1, '032b')]!=reg[format(rs2, '032b')] :
            pc = sing_to_bin(bin_to_sign(pc) + 4)
        else :
            v1 , v2 = bin_to_sign(pc), bin_to_sign(imm)
            pc = sing_to_bin(v1+v2)
    elif f3=="001" :
        if reg[format(rs1, '032b')]!=reg[format(rs2, '032b')] :
            v1 , v2 = bin_to_sign(pc), bin_to_sign(imm)
            pc = sing_to_bin(v1+v2)
        else :
            pc = sing_to_bin(bin_to_sign(pc) + 4)
    else :
        print("not valid f3 for b-type")
        sys.exit()

def J_type(instr):
    global pc
    opcode = instr[-7:]
    rd = instr[20:25]
    imm = instr[0] + instr[12:20] + instr[11] + instr[1:11] + "0"  
    imm =sign_ext(imm, 20, 32)
    reg[27*"0" +rd] = sing_to_bin(bin_to_sign(pc) + 4)
    pc = sing_to_bin(bin_to_sign(pc)+ bin_to_sign(imm)) 
    
def output_register(output_file):
    global pc, reg
    register_values = ["0b" + format(int(pc, 2), '032b')] + ["0b" + reg[format(i, '032b')] for i in range(32)]
    with open(output_file, "a") as f:
        f.write(" ".join(register_values) + " \n")

def output_memory(output_file):
    
    extras = []
    for i in memory.keys():
        if(i not in mem_keys):
            extras.append(i)
    for j in extras:
        del memory[j]
    with open(output_file, "a") as f:
        for address, value in sorted(memory.items()):
            f.write(f"{address}:{value}\n")

def error_handling(instr):
    global pc
    if (len(instr)!= 32):
        print("Invalid instruction length")
        sys.exit()
    
    opcode=instr[-7:]
    valid_opcodes= ("0110011", "0100011", "0000011", "0010011", "1100111", "1100011", "1101111")
    
    if (opcode not in valid_opcodes):
        print("Invalid opcode:", opcode)
        sys.exit()
    

    
    if (int(pc,2)%4!=0):
        print("PC not multiple of four")
        sys.exit()
    if (opcode =="1100011"):
        imm =instr[0]+ instr[24]+instr[1:7] +instr[20:24]
        if (int(imm,2)%2!=0):
            print("Branch misalignment")
            sys.exit()

def main():
    global pc
    pc = imm_conver(0,32)
    # output_file = "output.txt"
    while(int(pc,2)//4 < len(instructions) and instructions[int(pc,2)//4] != "00000000000000000000000001100011"):
        instr = instructions[int(pc,2)//4]
        oppcode = instr[-7:]
        error_handling(instr)
        if(oppcode == "0110011"):
            R_type(instr)
        elif(oppcode == "0100011"):
            S_type(instr)
        elif(oppcode in ["0000011","0010011","1100111"] ):
            I_type(instr)
        elif(oppcode == "1100011"):
            B_type(instr)
        elif(oppcode == "1101111"):
            J_type(instr)
        else:
            print("not valid oppcode")
        output_register(outputf)
    output_register(outputf)
    output_memory(outputf)

main()