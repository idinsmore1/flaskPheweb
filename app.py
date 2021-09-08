import json
import csv
import MySQLdb
import plotly
from flask import Flask, render_template, request, Response, redirect

from gwas_class import GwasData
from phewas import PhewasData

app = Flask(__name__)
conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
cursor = conn.cursor()


def relative_redirect(url: str) -> Response:
    return redirect(url, Response=RelativeResponse)


class RelativeResponse(Response):
    autocorrect_location_header = False


@app.route('/go')
def go():
    query = request.args.get('query', None)
    if query == 'pheno':
        return relative_redirect(f'/pheno/571')
    elif query == 'variant':
        return relative_redirect(f'/variant/22:43945024:C:T')
    else:
        return relative_redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "GET":
        languages = ["C++", "Python", "PHP", "Java", "C", "Ruby",
                     "R", "C#", "Dart", "Fortran", "Pascal", "Javascript"]

        return render_template("navbar2.html", languages=languages)


@app.route('/pheno/<pheno>')
def phenotype(pheno):
    pheno = pheno.replace('-', '_')
    data = GwasData(f'{pheno}', conn)
    fig = data.manhattan_plot()
    df = data.top_results
    pheno_info = data.pheno_info()
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('gwas_base.html',
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
                           zip=zip)


@app.route('/variant/<variant>')
def variation(variant):
    var = PhewasData(f'{variant}', conn)
    fig = var.phewas_plot()
    info = var.variant_info
    df = var.top_results
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('phewas_base.html',
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


# @app.route('/')
# def table():
#     data = GwasData(f'571', conn)
#     df = data.top_results
#     return render_template('table_structure.html',
#                            column_names=df.columns.values,
#                            row_data=list(df.values.tolist()),
#                            id_col='VarID',
#                            gene_col='Gene',
#                            zip=zip)


# @app.route('/download/<pheno>', methods=['GET'])
# def download(pheno):
#     pheno = pheno.replace('-', '.')
#     query = f"""SELECT v.*, g.MAF, g.EFFECTSIZE, g.SE, g.LOG10P
#                             FROM private_dash.TM90K_LOGP_gt2 g
#                             INNER JOIN private_dash.TM90K_variants v
#                             USING(VAR_ID)
#                             WHERE PHECODE = '{pheno}'"""
#     data = cursor.execute(query)
#     (file_basename, server_path, file_size) = create_csv(data, pheno)
#
#     return_file = open(server_path + file_basename, 'r')
#     response = make_response(return_file, 200)
#     response.headers['Content-Description'] = 'File Transfer'
#     response.headers['Cache-Control'] = 'no-cache'
#     response.headers['Content-Type'] = 'text/csv'
#     response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
#     response.headers['Content-Length'] = file_size
#     return response


if __name__ == '__main__':
    app.run(debug=True)
