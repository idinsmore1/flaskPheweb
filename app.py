import json
import os
import MySQLdb
import plotly
from flask import Flask, render_template, request, Response, redirect, send_from_directory

from static.utilites.gwas_class import GwasData
from static.utilites.phewas import PhewasData
from static.utilites.autocompletion import Autocompleter

app = Flask(__name__)
conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT PHECODE, phenotype FROM private_dash.TM90K_phenotypes')
phenos = {item[0].replace('_', '.'): {'phenostring': item[1]} for item in cursor.fetchall()}
cursor.close()

autocompleter = Autocompleter(phenos)


# def end(message='no message', exception=None):
#     if exception is not None:
#         print('Exception:', exception)
#         traceback.print_exc()
#     print(message, flush=True)
#     flash(message)
#     abort(404)


def relative_redirect(url: str) -> Response:
    return redirect(url, Response=RelativeResponse)


class RelativeResponse(Response):
    autocorrect_location_header = False


@app.route('/go')
def go():
    query = request.args.get('query', None)
    # if query is None:
    #     end('You\'ve submitted a null query, please try again.')
    best_suggestion = autocompleter.get_best_completion(query)
    if best_suggestion:
        return relative_redirect(best_suggestion['url'])
    # end(f"Couldn't find page for {query}")


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html',
                           page_title='UNGATED')


@app.route('/pheno/<pheno>')
def phenotype_page(pheno):
    pheno = pheno.replace('.', '_').replace('-', '_')
    data = GwasData(f'{pheno}', conn)
    fig = data.manhattan_plot()
    df = data.top_results
    pheno_info = data.pheno_info()
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('gwas_extend.html',
                           phenotype=pheno_info['phenotype'],
                           phecode=pheno_info['PHECODE'],
                           cases=pheno_info['cases'],
                           controls=pheno_info['controls'],
                           category=pheno_info['category'],
                           graphJSON=graphjson,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           id_col='VarID',
                           gene_col='Gene',
                           ref_col='HGVSc',
                           zip=zip)


@app.route('/variant/<variant>')
def variation(variant):
    var = PhewasData(f'{variant}', conn)
    fig = var.phewas_plot()
    info = var.variant_info
    df = var.top_results
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('phewas_extend.html',
                           variant=info['VAR_ID'],
                           gene=info['GENE'],
                           impact=info['IMPACT'],
                           effect=info['EFFECT'],
                           graphJSON=graphjson,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           pheno_col='phenotype',
                           pheno_dict=var.phecode_dict,
                           zip=zip)


@app.route('/phenotypes')
def phenotypes():
    return render_template('phenotypes_rendered.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
