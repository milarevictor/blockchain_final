def generate_events(num_events, simulation, time=0):
    events = 0
    while(events <= num_events):
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
      for i in range(1000):
          values.append(np.random.exponential(scale=10))

      next_time_generate = round(np.average(values))
      miners = []
      probability_distribution = []
      num_miners = simulation.blockchain.get_num_info(time)['num_miners']
      miner_prob = minersCP/totalCP
      user_prob = userCP/totalCP
      for i in range(num_miners):
          miners.append('m')
          probability_distribution.append(miner_prob)
      miners.append('u')
      probability_distribution.append(user_prob)
      miner_choice = choice(miners, 1, p=probability_distribution)
      while minutes <= next_time_generate:
        if(minutes == next_time_generate):
          block = Block(blockchain=simulation.blockchain)
          block.save()
          last_id = Event.objects.filter(
              blockchain=simulation.blockchain).latest('event_id').event_id
          event = Event(time=time, event_id=last_id+1, typeOfEvent=1,
                        blockchain=simulation.blockchain, block=block)
          event.save()
          events += 1
          if(miner_choice == 'u'):
            message = str(time) + ' dias(s): Bloco minerado pelo usuário.'
          else:
            message = str(time) + \
                          ' dias(s): Bloco minerado por um minerador.'
          log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
                        message=message)
          log.save()
        miners_entered = np.random.poisson(simulation.lambda_prob, 1/24)[0]
        for i in range(miners_entered):
              miner = Miner(blockchain=simulation.blockchain,
                            computPower=minersCP)
              miner.save()
              last_id = Event.objects.filter(
                  blockchain=simulation.blockchain).latest('event_id').event_id
              event = Event(time=time, event_id=last_id + 1, typeOfEvent=3, miner=miner,
                            blockchain=simulation.blockchain)
              event.save()
              message = str(time) + ' dia(s): Inserção de minerador.'
              log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
                        message=message)
              log.save()
              events += 1
        time += 1/24













   while time < next_time_generate:
        # time deve ser dado em dias
        time += 1
        # try:
        #     block_time = Event.objects.filter(
        #         blockchain=simulation.blockchain).filter(typeOfEvent=1).latest('event_id').time
        # except:
        #     block_time = 0
        # time_interval = time - block_time
        # # Abaixo eu defini o lambda de Poisson como 0.3
        # miners_entered = np.random.poisson(simulation.lambda_prob, 1)[0]
        # prob = 1 - math.exp(-1*userCP*time_interval*24*3600/dificuldade)
        # if prob > 0.5:
        #     block = Block(blockchain=simulation.blockchain)
        #     block.save()
        #     last_id = Event.objects.filter(
        #         blockchain=simulation.blockchain).latest('event_id').event_id
        #     event = Event(time=time, event_id=last_id+1, typeOfEvent=1,
        #                   blockchain=simulation.blockchain, block=block)
        #     event.save()
        #     message = str(int(time)) + ' dias(s): Bloco minerado.'
        #     log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
        #               message=message)
        #     log.save()
        #     events += 1
        # for i in range(miners_entered):
        #     miner = Miner(blockchain=simulation.blockchain,
        #                   computPower=minersCP)
        #     miner.save()
        #     last_id = Event.objects.filter(
        #         blockchain=simulation.blockchain).latest('event_id').event_id
        #     event = Event(time=time, event_id=last_id + 1, typeOfEvent=3, miner=miner,
        #                   blockchain=simulation.blockchain)
        #     event.save()
        #     message = str(int(time)) + ' dia(s): Inserção de minerador.'
        #     log = Log(event_id=event.event_id, blockchain=simulation.blockchain,
        #               message=message)
        #     log.save()
        #     events += 1
    return simulation.blockchain.get_num_info(time)
