from django.shortcuts import render
from simulator.models import Simulation, Blockchain, Block, Event, User, Miner
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from simulator.forms import createSimulForm
from django.http import JsonResponse
import datetime
import math
import numpy as np
from numpy.random import choice
import xlwt
from django.http import HttpResponse
from Crypto.Cipher import AES
import base64
import math

MASTER_KEY = "blockchain-simulator-encryption-key"


def encrypt_val(clear_text):
    enc_secret = AES.new(MASTER_KEY[:32])
    tag_string = (str(clear_text) +
                  (AES.block_size -
                   len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))

    return cipher_text


def decrypt_val(cipher_text):
    dec_secret = AES.new(MASTER_KEY[:32])
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
    clear_val = raw_decrypted.decode().rstrip("\0")
    return clear_val


def create_simul(request):
    if request.method == "POST":
        dados = request.POST
        return JsonResponse(dados)
    return render(request, 'simulator/start.html')


def plotGraph(time, sid):
    # Set initial variables
    data = []
    label = []
    # Get objects
    simulation = Simulation.objects.get(id=sid)
    blockchain = simulation.blockchain
    user = simulation.user
    # Get params
    energyCost = simulation.energyCost
    energyCons = simulation.energyCons
    reward = blockchain.reward
    avg_time = blockchain.avg_time
    # Get variables
    totalCP = blockchain.get_total_cp(time)
    # Do the math
    num_miners = Miner.objects.filter(blockchain=blockchain).count()
    for time_interval in range(1801):
        time_interval_temp = time_interval
        # Ajustamos a média da poisson para o período de 1 dia
        miner_entered = np.random.poisson(
            simulation.lambda_prob*24*(1 - math.exp((-1)/num_miners)))
        num_miners += miner_entered
        totalCP += miner_entered*simulation.minersCP
        # Estamos calculando o numero de blocos encontrados em média pelo usuário por unidade de tempo calculado em blocos por hora
        blocos_por_tempo_med = 60*user.computPower*time_interval / \
            (totalCP*avg_time)
        custo = energyCost*energyCons*time_interval*3600
        ganho_esperado = (reward)*blocos_por_tempo_med - custo
        data.append(int(ganho_esperado))
        log_string = ''
        if time_interval >= 360:
            log_string += str(int(time_interval//360)) + "a  "
            time_interval = time_interval % 360
        if time_interval >= 30:
            log_string += str(int(time_interval/30)) + "m  "
            time_interval = time_interval % 30
        if time_interval > 0:
            log_string += str(int(time_interval)) + "d"
        label.append(log_string)
        time_interval = time_interval_temp
    min_value = min(data)
    max_value = max(data)
    steps = (max_value - min_value)/10
    dados = {'label': label, 'data': data,
             'min_value': min_value, 'max_value': max_value, 'steps': steps}
    return dados


def save_blockchain(request):
    simulation_id = request.GET['sid']
    # simulation_id.strip("-")
    # print(simulation_id)
    content = encrypt_val(simulation_id)
    response = HttpResponse(
        content, content_type='application/force-download; charset=utf8')
    response['Content-Disposition'] = 'attachment; filename="blockchain_details.bds"'
    return response


# def load_blockchain(file):


def get_log(request):
    if request.method == "GET":
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="blockchain_log.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("Log")
        row_num = 0
        font_style = xlwt.XFStyle()

        font_style.font.bold = True
        columns = ['Event type', 'Time', 'Miner (if applies)']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        simulation_id = request.GET['sid']
        simulation = Simulation.objects.get(id=simulation_id)
        blockchain = simulation.blockchain
        event = int(request.GET['e'])
        events = Event.objects.filter(
            blockchain=blockchain).filter(event_id__lte=event)
        for event_row in events:
            row_num = row_num + 1
            ws.write(row_num, 0, event_row.get_typeOfEvent_display(), font_style)
            ws.write(row_num, 1, event_row.time, font_style)
            if event_row.typeOfEvent == 1 and event_row.miner == 'user':
                ws.write(row_num, 2, 'User', font_style)
            else:
                ws.write(row_num, 2, '-', font_style)

        dados = dict()
        wb.save(response)
        return response


def start_simul(request):
    if request.is_ajax():
        simulation_id = request.GET['sid']
        event = request.GET['e']
        time = request.GET['t']
        button = request.GET['operation']
        simulation = Simulation.objects.get(id=simulation_id)
        blockchain = simulation.blockchain
        latest_time = Event.objects.filter(
            blockchain=blockchain).latest('time').time
        latest_event = Event.objects.filter(
            blockchain=blockchain).count()
        if button == 'next_time':
            if int(time) < 0:
                time = 0
            while int(time) > latest_time:
                generate_events(180, simulation, latest_time)
                latest_time = Event.objects.filter(
                    blockchain=blockchain).latest('time').time
            num_events = Event.objects.filter(
                blockchain=simulation.blockchain).filter(time__lte=time).count()
        if button == 'next_event':
            if int(event) < 1:
                event = 1
            num_events = event
            if int(event) > latest_event:
                events_to_generate = int(event)-latest_event
                generate_events(events_to_generate, simulation, latest_time)
                time = Event.objects.filter(
                    blockchain=blockchain).filter(event_id=int(event)).first().time
            else:
                time = Event.objects.filter(
                    blockchain=blockchain).filter(event_id=int(event)).first().time
        dados = simulation.blockchain.get_num_info(time=time)
        print(dados)
        dados['time'] = int(time)
        dados['num_forks'] = Event.objects.filter(
            blockchain=blockchain).filter(typeOfEvent=5).count()
        dados['num_blocks'] = Block.objects.filter(
            blockchain=blockchain).count()
        dados['num_miners'] = Miner.objects.filter(
            blockchain=blockchain).count()
        dados['num_events'] = num_events
        dados_graph = plotGraph(time=time, sid=simulation_id)
        dados['dados_graph'] = dados_graph
        return JsonResponse(dados)
    if request.method == "POST":
        if 'uploaded1' in request.FILES:
            upload1 = request.FILES['uploaded1'].read()
            data1 = ""
            for x in upload1:
                data1 = data1 + chr(x)
            # print(decrypt_val(data1))
            simulation = Simulation.objects.filter(
                id=decrypt_val(data1)).first()
            if simulation:
                blockchain = simulation.blockchain
                num_events = Event.objects.filter(
                    blockchain=blockchain).count()
                num_miners = Miner.objects.filter(
                    blockchain=blockchain).count()
                num_blocks = Block.objects.filter(
                    blockchain=blockchain).count()
                num_forks = Event.objects.filter(
                    blockchain=blockchain).filter(typeOfEvent=5).count()
                last_time = Event.objects.filter(
                    blockchain=blockchain).last().time
                dados = {"simulation_id": f'{simulation.id}',
                         "blockchain_id": f'{blockchain.id}',
                         "num_miners": num_miners,
                         "num_blocks": num_blocks,
                         "num_events": num_events,
                         "num_forks": num_forks,
                         "time": int(last_time)}
                print(dados)
                return render(request, 'simulator/index.html', context=dados)
        else:
            # Os próximos dados entrarão via post (formulário)
            avg_time = float(request.POST["avgTime"])
            # Custo dado em R$/kWh
            energCost = float(request.POST["energyCos"])
            # Consumo de energia dado em kW
            energCons = float(request.POST["energyCons"])
            # Poder computacional dado em TH/s
            ownCP = float(request.POST["ownCP"])
            minersCP = float(request.POST["minersCP"])
            reward = float(request.POST["reward"])
            lambda_prob = float(request.POST["medProb"])
            name = request.POST['simulName']

            # A partir daqui crio a blockchain, simulação, usuário e seto o primeiro minerador
            blockchain = Blockchain(avg_time=avg_time, reward=reward)
            blockchain.save()
            user = User(computPower=ownCP)
            user.save()
            simulation = Simulation(blockchain=blockchain, name=name,
                                    energyCons=energCons, minersCP=minersCP, lambda_prob=lambda_prob, energyCost=energCost, user=user)
            simulation.save()
            start_miner = Miner(blockchain=blockchain,
                                computPower=minersCP)
            start_miner.save()
            event = Event(time=0, typeOfEvent=3, miner=start_miner,
                          blockchain=blockchain)
            event.save()
            message = str(int(0)) + ' hora(s): Inserção de minerador.'

            num_dados = generate_events(0, simulation)

            dados = {"simulation_id": f'{simulation.id}',
                     "blockchain_id": f'{blockchain.id}',
                     "num_miners": num_dados['num_miners'],
                     "num_blocks": num_dados['num_blocks'],
                     "num_events": num_dados['num_events'],
                     "num_forks": num_dados['num_forks'],
                     "time": "0", }
            dados_graph = plotGraph(time=0, sid=simulation.id)
            dados['dados_graph'] = dados_graph
            dados['simul_name'] = simulation.name
            return render(request, 'simulator/index.html', context=dados)
    else:
        return render(request, 'simulator/start.html')


def generate_events(num_events, simulation, time=0):
    events = 0
    while(events < num_events):
        # O valor do minerCP em MHash/s
        minersCP = simulation.minersCP
        # computPower em MHash/s
        userCP = simulation.user.computPower
        # TotalCP em MHash/s
        totalCP = simulation.blockchain.get_total_cp(time)
        # Average time em minutos
        avg_time = simulation.blockchain.avg_time
        # Cálculo da dificuldade com total MHash
        dificuldade = totalCP*avg_time*60
        values = []
        for i in range(5):
            values.append(np.random.exponential(scale=10))
        interval = round(np.average(values))
        time += interval
        have_fork = np.random.poisson(0.1*interval)
        if(have_fork > 1):
            last_id = Event.objects.filter(
                blockchain=simulation.blockchain).latest('event_id').event_id
            event = Event(time=time, event_id=last_id+1, typeOfEvent=5,
                          blockchain=simulation.blockchain)
            event.save()

        num_miners = simulation.blockchain.get_num_info(time)['num_miners']
        user_prob = userCP/totalCP
        random_num = np.random.random_sample()
        last_id = Event.objects.filter(
            blockchain=simulation.blockchain).latest('event_id').event_id

        block = Block(blockchain=simulation.blockchain)
        block.save()

        events += 1
        if(random_num <= user_prob):

            event = Event(time=time, event_id=last_id+1, typeOfEvent=1,
                          blockchain=simulation.blockchain, block=block, miner='user')
            event.save()

        else:
            event = Event(time=time, event_id=last_id+1, typeOfEvent=1,
                          blockchain=simulation.blockchain, block=block)
            event.save()

        for i in range(int(interval)):
            miner_entered = np.random.poisson(
                simulation.lambda_prob)
            if(miner_entered > 0):
                for miner in range(miner_entered):
                    miner = Miner(blockchain=simulation.blockchain,
                                  computPower=minersCP)
                    miner.save()
                    last_id = Event.objects.filter(
                        blockchain=simulation.blockchain).latest('event_id').event_id
                    event = Event(time=time + i, event_id=last_id + 1, typeOfEvent=3, miner=miner,
                                  blockchain=simulation.blockchain)
                    event.save()

            events += 1

    return simulation.blockchain.get_num_info(time)
