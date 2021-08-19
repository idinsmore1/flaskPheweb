from flask import Flask, render_template, url_for
from gwas_class import GwasData
import MySQLdb
import json
import plotly

import numpy as np

app = Flask(__name__)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/')
def test():
    conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
    data = GwasData('250_2', conn)
    fig = data.manhattan_plot()
    df = data.top_results
    pheno_info = data.pheno_info()
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    rendered_html = render_template('gwas_base.html',
                                    phenotype=pheno_info['phenotype'],
                                    phecode=pheno_info['PHECODE'],
                                    cases=pheno_info['cases'],
                                    controls=pheno_info['controls'],
                                    category=pheno_info['category'],
                                    graphJSON=graphjson,
                                    column_names=df.columns.values, row_data=list(df.values.tolist()),
                                    link_column='VAR_ID', zip=zip)
    return rendered_html


@app.route('/nav')
def nav():
    return render_template('navbar.html')


# @app.route('/<phenotype>')
# def pheno_page(phenotype):
#     return render_template(f'X{phenotype}.html')


if __name__ == '__main__':
    app.run()
