from json import dumps

import pandas as pd
from MySQLdb import connect
from jinja2 import Environment, FileSystemLoader
from plotly.utils import PlotlyJSONEncoder

from gwas_class import GwasData

conn = connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
query = 'SELECT DISTINCT PHECODE FROM private_dash.TM90K_phenotypes'
data = pd.read_sql(query, conn)
phecodes = [x for x in data.PHECODE]
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('gwas_base.html')

if __name__ == '__main__':
    for index, code in enumerate(phecodes):
        df = GwasData(code, conn)
        fig = df.manhattan_plot()
        table = df.top_results
        graphjson = dumps(fig, cls=PlotlyJSONEncoder)
        output = template.render(graphJSON=graphjson,
                                 column_names=table.columns.values, row_data=list(table.values.tolist()),
                                 link_column='VAR_ID', zip=zip)
        with open(f'templates/X{code}.html', 'w') as f:
            f.write(output)
        print(f'{index + 1}/{len(phecodes)} done!')
