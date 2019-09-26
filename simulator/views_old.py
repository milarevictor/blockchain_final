from django.shortcuts import render
from simulator.models import Simulation, Blockchain, Block, Event, User, Miner, Log
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from simulator.forms import createSimulForm
from django.http import JsonResponse
import datetime
import math
import numpy as np


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
    for time_interval in range(1801):
        time_interval_temp = time_interval
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


def get_log(request):
    if request.is_ajax():
        simulation_id = request.GET['sid']
        simulation = Simulation.objects.get(id=simulation_id)
        blockchain = simulation.blockchain
        event = int(request.GET['e'])
        log_set = []
        logs = Log.objects.filter(
            blockchain=blockchain).filter(event_id__lte=event)
        for log in logs:
            log_set.append(log.message)
        dados = dict()
        dados['log'] = log_set
        return JsonResponse(dados)


def start_simul(request):
    if request.is_ajax():
        simulation_id = request.GET['sid']
        # Ainda não configurei o log por evento
        event = request.GET['e']
        time = request.GET['t']
        button = request.GET['operation']
        simulation = Simulation.objects.get(id=simulation_id)
        blockchain = simulation.blockchain
        log_set = []
        latest_time = Event.objects.filter(
            blockchain=blockchain).latest('time').time
        latest_event = Event.objects.filter(
            blockchain=blockchain).count()
        if button == 'next_time':
            if int(time) < 0:
                time = 0
            while int(time) > latest_time:
                generate_events(100, simulation, latest_time)
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
        dados['time'] = time
        dados['num_events'] = num_events
        dados_graph = plotGraph(time=time, sid=simulation_id)
        dados['dados_graph'] = dados_graph
        return JsonResponse(dados)
    if request.method == "POST":
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
        start_miner = Miner(blockchain=blockchain, computPower=minersCP)
        start_miner.save()
        event = Event(time=0, typeOfEvent=3, miner=start_miner,
                      blockchain=blockchain)
        event.save()
        message = str(int(0)) + ' dia(s): Inserção de minerador.'
        log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
                  message=message)
        log.save()
        num_dados = generate_events(0, simulation)

        dados = {"simulation_id": f'{simulation.id}',
                 "blockchain_id": f'{blockchain.id}',
                 "num_miners": num_dados['num_miners'],
                 "num_blocks": num_dados['num_blocks'],
                 "num_events": num_dados['num_events']}
        dados_graph = plotGraph(time=0, sid=simulation.id)
        dados['dados_graph'] = dados_graph
        dados['simul_name'] = simulation.name
        return render(request, 'simulator/index.html', context=dados)
    else:
        return render(request, 'simulator/start.html')


def generate_events(num_events, simulation, time=0):
    events = 0
    # O valor do minerCP tá setado manualmente, virá do formulário depois
    minersCP = simulation.minersCP
    # computPower em Mhash/s
    userCP = simulation.user.computPower
    # TotalCP em Mhash/s
    totalCP = simulation.blockchain.get_total_cp(time)
    # Average time em minutos
    avg_time = simulation.blockchain.avg_time
    # Cálculo da dificuldade com total MHash
    dificuldade = totalCP*avg_time*60
    while events < num_events:
        # time deve ser dado em dias
        time += 1
        try:
            block_time = Event.objects.filter(
                blockchain=simulation.blockchain).filter(typeOfEvent=1).latest('event_id').time
        except:
            block_time = 0
        time_interval = time - block_time
        # Abaixo eu defini o lambda de Poisson como 0.3
        miners_entered = np.random.poisson(simulation.lambda_prob, 1)[0]
        prob = 1 - math.exp(-1*userCP*time_interval*24*3600/dificuldade)
        if prob > 0.5:
            block = Block(blockchain=simulation.blockchain)
            block.save()
            last_id = Event.objects.filter(
                blockchain=simulation.blockchain).latest('event_id').event_id
            event = Event(time=time, event_id=last_id+1, typeOfEvent=1,
                          blockchain=simulation.blockchain, block=block)
            event.save()
            message = str(int(time)) + ' dias(s): Bloco minerado.'
            log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
                      message=message)
            log.save()
            events += 1
        for i in range(miners_entered):
            miner = Miner(blockchain=simulation.blockchain,
                          computPower=minersCP)
            miner.save()
            last_id = Event.objects.filter(
                blockchain=simulation.blockchain).latest('event_id').event_id
            event = Event(time=time, event_id=last_id + 1, typeOfEvent=3, miner=miner,
                          blockchain=simulation.blockchain)
            event.save()
            message = str(int(time)) + ' dia(s): Inserção de minerador.'
            log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
                      message=message)
            log.save()
            events += 1
    return simulation.blockchain.get_num_info(time)
