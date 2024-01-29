from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from pytz import timezone
import time
import pandas as pd
import sys

email = str(input("escreva o seu email: "))
senha = str(input("escreva a sua senha: "))
ativ = 'EURUSD'

def fazerConexao(email,senha,bala='PRACTICE'):
    
    API = IQ_Option(email,senha,bala)


    API.connect()
    API.change_balance(bala)

    conectado = False
    if API.check_connect() == True:
        print("Conexão estabelecida")
        conectado = True
    else:
        print("Erro de conexão")
        conectado = False
    return API, conectado

API, conectado=fazerConexao(email,senha,bala="PRACTICE")
info = API.get_profile_ansyc()

def timestamp(x, timezone_='America/Sao_Paulo'):
    d = datetime.fromtimestamp(x,tz=timezone(timezone_))
    return d

def inforConta(API):
    conta = API.get_profile_ansyc()
    nome = conta['name']
    moeda = conta['currency']
    data_cri = timestamp(conta['created'])
    id = conta['id']

    return nome,moeda,data_cri,id
nome,moeda,data_cri,id = inforConta(API)

def payout(par, tipo,API, timeframe = 1):
    if tipo == 'turbo':
        a = API.get_all_profit()
        g = int(100*a[par]['turbo'])
        return g
    elif tipo == 'digital':
        API.subscribe_strike_list(par, timeframe)
        while True:
            d = API.get_digital_current_profit(par,timeframe)
            if d != False:
                d = int(d)
                break
            time.sleep(1)
        API.unsubscribe_strike_list(par,timeframe)
        return d
ativos = API.get_all_open_time()
def coleta(ativ,API):
    velas = API.get_candles(ativ,60,3,time.time())
    velas[0] = 'A' if velas[0]['open'] < velas[0]['close'] else 'B' if velas[0]['open'] > velas[0]['close'] else 'D'
    velas[1] = 'A' if velas[1]['open'] < velas[1]['close'] else 'B' if velas[1]['open'] > velas[1]['close'] else 'D'
    velas[2] = 'A' if velas[2]['open'] < velas[2]['close'] else 'B' if velas[2]['open'] > velas[2]['close'] else 'D'
    cores = velas[0] + ' ' + velas[1] + ' ' + velas[2]
    return cores
r = coleta(ativ,API)

def direcional(cores):
    direcao = ''
    if cores.count('A') > cores.count('B') and cores.count('c')==0:
        direcao='put'
    if cores.count('B') > cores.count('A') and cores.count('c')==0:
        direcao = 'call'
    return direcao

def stop(lucro,stop_Gain, stop_loss):
    if lucro <= -stop_loss:
        print("atingiu o stop loss")
        sys.exit()
    if lucro >= stop_Gain:
        print("bateu a meta do dia")
        sys.exit()
    
def Martingale(entrada,payout):
    aposta = (entrada*(1+payout))/payout
    return aposta

stop_Gain = 10000
stop_loss = 3000
entrada = 1000
martingale = 2

trade = 0
stop_Gain = 10000
stop_loss = 3000
valor_entrada = entrada
martingale = 2
d = datetime.now(tz = timezone('America/Sao_Paulo'))
minutos = d.minute
horas = d.hour
segundos = d.second
entrar = 'False'
n_espera = 5
delay = 2
cont = 0
lucro = 0

while True:
    d = datetime.now(tz = timezone('America/Sao_Paulo'))
    minutos = d.minute
    horas = d.hour
    segundos = d.second
    novocandles = (segundos==(60-delay))
    if(novocandles):
        cont = cont + 1    
    print(ativ,', New Bar - ',novocandles, ' - Num Bar = ',cont,',seg = ',segundos,', Trade = ', trade)

    if cont == 5:
        entrar = True
        cont=0
    
    if entrar == True:
        print('\n\nATENÇÃO VAI SER EFETUADO A AÇÃO')
        print("VEREFICANDO CADLES")
        print('------------------------------------------')

        Velas = API.get_candles(ativ, 60, 3, time.time())

        cores = coleta(ativ,API)

        direcao = direcional(cores)

        if direcao == '':
            print('NÃO VAMOS REALIZAR')
        else:
            print('As cores foram: ',cores)
        if (direcao =='call' or direcao=='put'):
            print('direcao da aposta: ',direcao)

            entrada = valor_entrada
            for i in range(martingale+1):
                status,id_ = API.buy(entrada,ativ,direcao,1)
                cont +=1
                print('estamos posicionados numa ', direcao)
                trade +=1

                if status:
                    while True:
                        status,valor = API.check_win_v4(id_)

                        if status:
                            valor = valor if valor > 0 else float('-'+ str(abs(valor_entrada)))
                            lucro += round(valor,2)

                            print('--------------------------------------------------')
                            print('Resulatdo ',end='')
                            print(':: win |' if valor>0 else 'LOSS |', round(valor,2), '|',round(lucro,2))
                            print('--------------------------------------------------')

                            valor_entrada = Martingale(entrada,89)
                            stop(lucro,stop_Gain,stop_loss)

                            if (valor > 0 and i==martingale):
                                cont += 1
                                print("saimos no win")
                            
                            entrar = False
                            break
                    if valor > 0 : break
                else:
                    print("ERRO AO REALIZAR A OPERAÇÃO")
                if(i>0):
                    cont += 1
                print('Iterando = ',i,', tivemos um incremento por conta do gale')
                print("vamos operar mais um "+direcao+', com entrada de ', valor)
    time.sleep(1)
