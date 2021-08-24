from json import dumps
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from MySQLdb import connect
from plotly.utils import PlotlyJSONEncoder
from gwas_class import GwasData

# app = Flask(__name__)

conn = connect(user='dash_readonly', password='dashtest', host='ghsmfgwesdblx1v')
query = 'SELECT DISTINCT PHECODE FROM private_dash.TM90K_phenotypes'
code_query = pd.read_sql(query, conn)
phecodes = [x for x in code_query.PHECODE]
env = Environment(loader=FileSystemLoader('templates'))
page = env.get_template('gwas_base.html')

def generate_template(template, phenos):
    for index, code in enumerate(phenos):
        data = GwasData(code, conn)
        fig = data.manhattan_plot()
        df = data.top_results
        pheno_info = data.pheno_info()
        graphjson = dumps(fig, cls=PlotlyJSONEncoder)
        output = template.render(phenotype=pheno_info['phenotype'],
                                 phecode=pheno_info['PHECODE'],
                                 cases=pheno_info['cases'],
                                 controls=pheno_info['controls'],
                                 category=pheno_info['category'],
                                 graphJSON=graphjson,
                                 column_names=df.columns.values, row_data=list(df.values.tolist()),
                                 link_column='VAR_ID', zip=zip)
        with open(f'templates/X{code}.html', 'w') as f:
            f.write(output)
            print(f'{index + 1}/{len(phecodes)} done!')


if __name__ == '__main__':
    generate_template(page, phecodes)
