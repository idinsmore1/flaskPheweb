from flask import Flask, render_template
from gwas_class import GwasData
import MySQLdb
import json
import plotly

import numpy as np

app = Flask(__name__)


@app.route('/')
def line():
    conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
    data = GwasData('250_2', conn)
    fig = data.manhattan_plot()
    df = data.top_results
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    rendered_html = render_template('index.html',
                                    graphJSON=graphjson,
                                    column_names=df.columns.values, row_data=list(df.values.tolist()),
                                    link_column='VAR_ID', zip=zip)
    with open('templates/test_everything.html', 'w') as f:
        f.write(rendered_html)
    return rendered_html


@app.route('/test')
def test():
    return render_template('test_everything.html')


@app.route('/dataframe')
def dataframe():
    conn = MySQLdb.connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
    df = GwasData('250_2', conn).top_results
    return render_template('dataframe.html', column_names=df.columns.values, row_data=list(df.values.tolist()),
                           link_column='VAR_ID', zip=zip)


if __name__ == '__main__':
    app.run()
