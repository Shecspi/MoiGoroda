"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from account.report import CityReport
from account.serializer import TxtSerializer, CsvSerializer, JsonSerializer, XlsSerializer
from services import logger


@require_http_methods(['POST'])
@login_required()
def download(request):
    users_data = request.POST.dict()
    reporttype = users_data.get('reporttype')
    filetype = users_data.get('filetype')

    # Для того чтобы добавить новый формат репорта, достаточно создать класс,
    # реализующий интерфейс report.Report и добавить его эту секцию if ... else ...
    if reporttype == 'city':
        report = CityReport(request.user.id)
    # elif reporttype == 'region':
    #     report = RegionReport(request.user.id)
    # elif reporttype == 'area':
    #     report = AreaReport(request.user.id)
    else:
        logger.info(request, f'(Download stats): Incorrect reporttype "{reporttype}", raise 404')
        raise Http404

    # Для того чтобы добавить новый формат файла, достаточно создать класс,
    # реализующий интерфейс serialiizer.Serializer и добавить его эту секцию if ... else ...
    if filetype == 'txt':
        buffer = TxtSerializer()
    elif filetype == 'csv':
        buffer = CsvSerializer()
    elif filetype == 'json':
        buffer = JsonSerializer()
    elif filetype == 'xls':
        buffer = XlsSerializer()
    else:
        logger.info(request, f'(Download stats): Incorrect filetype "{filetype}", raise 404')
        raise Http404

    response = HttpResponse(
        buffer.convert(report.get_report()).getvalue(), content_type=buffer.content_type()
    )
    filename = f'MoiGoroda__{request.user}__{int(datetime.now().timestamp())}.{buffer.filetype()}'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    logger.info(request, f'(Download stats): Successfully downloaded file {filename}')

    return response
