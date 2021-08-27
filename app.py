import json

import MySQLdb
import plotly
from flask import Flask, render_template, url_for

from gwas_class import GwasData
from phewas import PhewasData

app = Flask(__name__)
conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')


@app.route('/')
def index():
    return render_template('index.html')


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
def variant(variant):
    var = PhewasData(f'{variant}', conn)
    fig = var.phewas_plot()
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('phewas_base.html',
                           graphJSON=graphjson)


@app.route('/test/table')
def table():
    data = GwasData(f'250_2', conn)
    df = data.top_results
    return render_template('table_structure.html', column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           id_col='VarID',
                           gene_col='Gene',
                           zip=zip)


@app.route('/gene/<gene>')
def gene(gene):
    return f'{gene}'


if __name__ == '__main__':
    app.run()
