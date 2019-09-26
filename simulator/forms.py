from django import forms


class createSimulForm(forms.Form):
    ownCP = forms.FloatField(label='Poder computacional do usuário (em MH/s)')
    minerCP = forms.FloatField(label='Poder computacional de cada minerador (em MH/s)')
    minersNum = forms.IntegerField(label='Número de mineradores')
    energCost = forms.FloatField(label='Custo energético (em R$/kWh)')
    energCons = forms.FloatField(label='Consumo médio (em kW)')
    avg_time = forms.FloatField(label='Tempo médio de geração (em minutos)')
    recompensa = forms.FloatField(label='Recompensa por bloco (em R$)')
