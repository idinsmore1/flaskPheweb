import json
import csv
import MySQLdb
import plotly
from flask import Flask, render_template, request

from gwas_class import GwasData
from phewas import PhewasData

app = Flask(__name__)
conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
cursor = conn.cursor()


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
#
#
# def create_csv(data, name):
#     """ returns (file_basename, server_path, file_size) """
#     file_basename = f'{name}_download.csv'
#     server_path = '/directory/subdirectory'
#     w_file = open(server_path + file_basename, 'w')
#     w_file.write('your data headers separated by commas \n')
#
#     for row in data:
#         row_as_string = str(row)
#         w_file.write(row_as_string[1:-1] + '\n')  ## row_as_string[1:-1] because row is a tuple
#
#     w_file.close()
#
#     w_file = open(server_path + file_basename, 'r')
#     file_size = len(w_file.read())
#     return file_basename, server_path, file_size

if __name__ == '__main__':
    app.run(debug=True)
