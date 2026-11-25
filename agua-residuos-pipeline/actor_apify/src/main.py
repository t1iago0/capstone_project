"""Punto de entrada del Actor de Apify: lee la entrada, predice y guarda los resultados en el dataset."""
from apify import Actor

from .inference import predecir

CAMPOS = ('nombre_municipio', 'poblacion', 'cobertura_agua_pct', 'toneladas_residuos_anuales')


async def main() -> None:
    async with Actor:
        entrada = await Actor.get_input() or {}

        lista = entrada.get('municipios')
        if lista:
            registros = list(lista)
        else:
            registros = [{c: entrada.get(c) for c in CAMPOS}]

        ok, con_error = 0, 0
        for registro in registros:
            try:
                resultado = predecir(registro)
                await Actor.push_data(resultado)
                ok += 1
            except ValueError as e:
                if len(registros) == 1:
                    raise                      # entrada única inválida: la corrida falla con el motivo en el log
                Actor.log.warning('Registro omitido: %s', e)
                await Actor.push_data({'error': str(e)})
                con_error += 1

        Actor.log.info('Predicciones generadas: %d | con error: %d', ok, con_error)
        await Actor.set_value('OUTPUT', {'predicciones': ok, 'con_error': con_error})
