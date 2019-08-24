import sys
import random
import crccheck
from Crypto.PublicKey import RSA

pra = RSA.importKey(open('./rsa_pri.pem').read())

#sys.stdout=open('./test_bit4096.txt','a')
#random.seed(0)
nbits = 4096
timer = 0   #

def genBigRam(bits):
    ret = 0
    mul = 1
    for i in range(bits):
        ran = random.randint(0, 1)
        #ran = 1
        ret = ret + ran * mul
        mul = mul * 2
    
    return ret


def expF(m, e, n): # binary method
    ret = 0
    e_str = str(bin(e))
    e_str = e_str[2:]
    len_e_str = len(e_str)
    
    if(e_str[0] == '1'):
        ret = m
    else:
        ret = 1
    
    for i in range(1, len_e_str):
        ret = ret * ret % n

        if(e_str[i] == '1'):
            ret = ret * m % n
            if(ret >= n):
                ret = ret % n
        
    return ret


def findRLen(n):
    r = 1
    i = 0
    while(r <= n):
        r = r * 2
        i = i + 1
    return i
    
# extende algorithm
def extGCD(a, b):
    #timer = time.clock()
    q_arr = []
    r_arr = []
    gcd = 1
    # reverse a and b if necessary
    fReversed = False
    if(a < b):
            fReversed = True
            temp = a
            a = b
            b = temp
    oa = a
    ob = b

    # get GCD
    while(a != 1):
            q = a / b
            q_arr.append(q)
            r = a % b
            r_arr.append(r)
            #print "& " + str(a) + " = " + str(b) + " * " + str(q) + " + " + str(r) + " & \\\\"

            if(r == 0):
                    gcd = b
                    break
            else:
                    a = b
                    b = r
    # get x and y
    x_arr = []
    y_arr = []
    x_arr.append(0)
    y_arr.append(1)
    x_arr.append(1)
    y_arr.append(-q_arr[0])
    x = 1
    y = -q_arr[0]
    #print "& " + str(r_arr[0]) + " = " +  str(oa) + " * " + str(x) + " + " + str(ob) + " * " + str(y) + " & \\\\"
    for i in range(1, len(q_arr)-1):
            x = (x_arr[i] * -q_arr[i] + x_arr[i - 1])
            y = (y_arr[i] * -q_arr[i] + y_arr[i - 1])
            x_arr.append(x)
            y_arr.append(y)
            #print "& " + str(r_arr[i]) + " = " +  str(oa) + " * " + str(x) + " + " + str(ob) + " * " + str(y) + " & \\\\"

    if(fReversed):
            temp = x
            x = y
            y = temp
    
    #print("extGCD time:")
    #print(time.clock() - timer)
    
    return [x, y, gcd]

def expMont(m, e, n): # montgomery method
    timer = 0
    ret = 0;
    r_len = findRLen(n)
    r = 1
    for i in range(r_len):
        r = r * 2
    
    [n_prime, r_prime, gcd] = extGCD(n, r)
    #print(extGCD(n, r))
    #print(str(n_prime * n + r_prime * r))
    
    n_prime = -n_prime  #required in expMontgomery
    #print('n_prime:%x'%int(n_prime))
#    print("n_prime")
#    print(n_prime)
    
    m_bar = (m << r_len) % n
    x_bar = r % n
#    print("m_bar:")
#    print(m_bar)
#    print("x_bar:")
#    print(x_bar)
    
    def monPro2(a_bar, b_bar):
        a_bar_str = str(bin(a_bar))
        a_bar_str = a_bar_str[2:]
        len_a_bar_str = len(a_bar_str)   

        res = 0     
        for i in reversed(range(len_a_bar_str)):
            if(a_bar_str[i] == "1"):
                res = res + b_bar
            if(res % 2 == 1):
                res = res + n
            res = res >> 1   
            
        for i in range(r_len - len_a_bar_str):
            if(res % 2 == 1):
                res = res + n
            res = res >> 1
        
        while(res >= n):
            res = res - n
            
        return res
    
    def monPro(a_bar, b_bar):
#        print("In monPro:")
        t = a_bar * b_bar
        m1 = t * n_prime
        m2 = ((m1 >> r_len) << r_len) ^ m1 # mod r
        m3 = m2 * n
        m4 = m3 + t
        #m = m % r
        u = m4 >> r_len

        while(u >= n):
            u = u - n    
                   
        return u
    
    e_str = str(bin(e))
    e_str = e_str[2:]
    len_e_str = len(e_str)
    for i in range(len_e_str):
        x_bar = monPro2(x_bar, x_bar)
        #print(i)
        #print('x_bar:'+hex(x_bar))
        if(e_str[i] == "1"):
            x_bar = monPro2(m_bar, x_bar)
            #print('x_bar_1:'+hex(x_bar))
                         

    ret = monPro2(x_bar, 1)
    return ret

def generate_t(a,b):
    if a < b:
        # a < b return x
        if a == 1:
            return 1
        else:
            # mid is value of y
            mid = generate_t(a, b % a)

            return int((b * mid + 1) // a)
    if a > b:
        # need return y
        # mid is value of x
        if b == 1:
            return a - 1
        else:
            mid = generate_t(a % b, b)

            return int((a * mid - 1) // b)



data_width = 64
addr_width = 64
total_width = 4096
#     n = 0
#     while n % 2 == 0:
#         n = random.randint(1, 2**total_width -1)
# e = 0xb

# m = random.randint(1,  n-1)
# d=  0x9BF98D153DD9275E6D8B3DD46AED1F57AC9A9571A8A4CB81C1EA1DD845FA8150D93006A28434E39E1ABD72165CF4CF97187E156ED9E77C24B1CBAA0AB4266B043292C4A65A115A7AAC6B3F038D628C58C420897EF4DEFBFB4513D92385C4B91FC7FCC51E6DDA665530A7E24D0E9D6AD62516876D28D6A6A856BAB403BC9E6B6A96B5F5B325D206EC21CF52138BA99853A000287E79102B9CFCF94D9A06ED1C351A2AE1FD8E9F03117CB547672844742FE31B3795DB0B8476B895729551F116F5527E1A33D2016EEC2E5E41882A6410A9522B6171533B988FEAB8979ECD5BF9EAFBA949779B305A1D122E30B896258D191B553AB5685C507D931FB5271A68467612A15E478822E6735CB478710E757C2A254FB0FEE12B76F6572F81326202DF07A78C3E0423A5D9BFEA5753A545D966930DFFF4F5DEBB099C20C9F07801BFA453C673EB379A6469A26C7E9BFC811BBA5847F1A8A946CED91AE4A163E93F54827F3B1FFA247C9C2E3E452D108060E44B1AC33084DA53CE61C577EB400074F00AC28FEE7B03F2C3F21313330DBA834D0A9B7976DC53FE86A1D323FF5020C8062B01606C3FBF6A6D94CA2316FF145CD9DD76B109E224D5CC6AC2B4DC1563BFFBD8E92770A96562665E174D7FAC6ED5B58D8447E9C7F1072BF05E30CEB22158F304EE28B10D3274AA32949FBE18021337A4F4772FABC6913D5F6B995609F6039BF1C1
n = pra.n
e = pra.e
m = 0x1538ebf833ffca2a01d6099faccea21238473afba693cba063edfe4c6a420c5fdbf3ac9b4cb158b976bedecb0f5cc9f6790c9d0b82a0d6617f997187fc6430c741c55e70053d277019f8f545b232d99ddd4c69b4933d6da4dd6a6aa267be8bbe210ee6d8d74e385085f9287c88651b8c7c7f4eabdd72a56e88a8566810d6cb4b6c5081f9fe41f724c144be319716c10ea90f7f13e13c8e2f8f3fed6bd5114ef59d6aed976139c406b8b84bd39c817f7be7375c6301d576a70a39166bbc1fd9dbfb3b72288cf7d62645319e16d198dffcea582172f82a0b469be7b6bca824fb01b048e684ff74570c42d8b96932a3abfa7abec98994ff73fd775a494d359fde93721784e43d32c4d0e351f606e2589e6030dd8f3e85d2e041b47e83821b916a7103f3080758b96a8d733775500af28f584c456d4416e73a647fd1232d2c1bd74abe03777e465bae8ac4ccbe3ed481fc4067c3fa6affed1ca6c68e84221cb24a486b01cc69a92576c6f53e6929c941f4dcd53b27950d72874f800cb89032af30742bb779eabc3aed51c2d295cdb6ae61d3e92dd706e2da462bcc036c3c06d32028235fe54ccdb2cd04c8d363a13fb8ad665bb6ee6aa2bb11fa1166b67cb38922295e23c407e58028fe69e5fc40db3198a0d21ba6e0d1161f950a63737aa53a9a793bd8d89ae83054d5d6b5b79e226e1a9e427042c2f9bb5f2deeb092d5a9cbd82c

a = 2 ** addr_width
b = n & (2**addr_width-1)
nprime = generate_t(a, b)
print('nprime = %d\'h%x;' % (data_width,nprime))
r1 = 2 ** total_width % n
print('r_in = %d\'h%x;'%(total_width,r1))
t1 = 2 ** (total_width * 2) % n
print('t_in = %d\'h%x;'%(total_width,t1))


d = pra.d


print('M_in = %d\'h%x;' % (total_width,m))
print('E_in = %d\'h%x;' % (total_width,e))
print('N_in = %d\'h%x;' % (total_width,n))
print('D_in = %d\'h%x;' % (total_width,d))
print("m^e mod n:\t")
# print('normol:'+hex(m**e%n))
repeats = 1
for i in range(repeats):
    m_2_e_mod_n = expMont(m, e, n)
print("Montgomery:" + hex(m_2_e_mod_n))

print('______________________')

TX_nprime = '070c' + str(hex(nprime))[2:]


raw_data = bytes.fromhex(TX_nprime)

crcinst = crccheck.crc.Crc16CcittFalse()
crcinst.process(raw_data)
TX_nprime = TX_nprime + str(crcinst.finalhex())


print('\nr_in = ')
for i in range(0,8):
    TX_r = '0544' + str(hex(d))[2+128 * i:130 + 128 * i]
    crcinst = crccheck.crc.Crc16CcittFalse()
    crcinst.process(bytes.fromhex(TX_r))
    TX_r = TX_r + str(crcinst.finalhex())
    print(TX_r)

print('\nt_in = ')
for i in range(0,8):
    TX_t = '0644' + str(hex(d))[2+128 * i:130 + 128 * i]
    crcinst = crccheck.crc.Crc16CcittFalse()
    crcinst.process(bytes.fromhex(TX_t))
    TX_t = TX_t + str(crcinst.finalhex())
    print(TX_t)

print('\nM_in = ')
for i in range(0,8):
    TX_m = '0144' + str(hex(m))[2+128 * i:130 + 128 * i]
    crcinst = crccheck.crc.Crc16CcittFalse()
    crcinst.process(bytes.fromhex(TX_m))
    TX_m = TX_m + str(crcinst.finalhex())
    print(TX_m)


print('\nD_in = ')
for i in range(0,8):
    TX_D = '0344' + str(hex(d))[2+128 * i:130 + 128 * i]
    crcinst = crccheck.crc.Crc16CcittFalse()
    crcinst.process(bytes.fromhex(TX_D))
    TX_D = TX_D + str(crcinst.finalhex())
    print(TX_D)

print('\nN_in = ')
for i in range(0,8):
    TX_N = '0444' + str(hex(n))[2+128 * i:130 + 128 * i]
    crcinst = crccheck.crc.Crc16CcittFalse()
    crcinst.process(bytes.fromhex(TX_N))
    TX_N = TX_N + str(crcinst.finalhex())
    print(TX_N)

print('96h\''+TX_nprime)





