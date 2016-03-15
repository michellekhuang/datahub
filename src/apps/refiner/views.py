from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.finders import find
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

from distill import inference


'''
@author: Anant Bhardwaj
@date: Mar 21, 2013

Datahub Refiner
'''


@login_required
def index(request):

    # load data from static files and pass it to the view
    crime_training_input = file(find('crime/input.txt')).read()
    crime_training_output = file(find('crime/output.txt')).read()
    crime_test = file(find('crime/test.txt')).read()

    hadoop_training_input = file(find('hadoop/input.txt')).read()
    hadoop_training_output = file(find('hadoop/output.txt')).read()
    hadoop_test = file(find('hadoop/test.txt')).read()

    return render_to_response("refiner.html", {
        'login': request.user.get_username(),
        'crime_training_input': crime_training_input,
        'crime_training_output': crime_training_output,
        'crime_test': crime_test,
        'hadoop_training_input': hadoop_training_input,
        'hadoop_training_output': hadoop_training_output,
        'hadoop_test': hadoop_test,
    })


@csrf_exempt
def refine_data(request):
    res = {'error': None}
    try:
        if request.method == 'POST':
            training_input = request.POST['training_input']
            training_output = request.POST['training_output']
            test_data = request.POST['test_data']
            record_separator = '\n'
            if 'record_separator' in request.POST:
                record_separator = request.POST['record_separator']

            o_fields_structure, i_structure = inference.learn_mapping(
                training_input, training_output)
            out = inference.extract(
                test_data, o_fields_structure, sep=record_separator)

            csv_lines = []
            for row in out:
                csv_lines.append(','.join(row.values()))

            csv_str = '\n'.join(csv_lines)
            res['output'] = csv_str
        else:
            res['error'] = 'Invalid HTTP Method'
    except Exception, e:
        res['error'] = str(e)

    return HttpResponse(json.dumps(res), content_type="application/json")
