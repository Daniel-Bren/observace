
import logging
import time

import requests

logger = logging.getLogger(__name__)

MAX_TENTATIVAS = 3
TIMEOUT = (5, 20)

STATUS_TRANSITORIOS = {429, 500, 502, 503, 504}


def consultar_tce(url, parametros):
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = requests.get(
                url,
                params=parametros,
                timeout=TIMEOUT
            )

            if (
                resposta.status_code in STATUS_TRANSITORIOS
                and tentativa < MAX_TENTATIVAS
            ):
                logger.warning(
                    "HTTP_TRANSITORIO | status=%s | tentativa=%s",
                    resposta.status_code,
                    tentativa
                )
            else:
                resposta.raise_for_status()
                return resposta.json()

        except (requests.ConnectionError, requests.Timeout) as erro:
            if tentativa == MAX_TENTATIVAS:
                raise

            logger.warning(
                "FALHA_HTTP | tentativa=%s | erro=%s",
                tentativa,
                erro.__class__.__name__
            )

        espera = 2 ** (tentativa - 1)
        time.sleep(espera)