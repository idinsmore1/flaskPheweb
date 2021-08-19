import numpy as np
import pandas as pd
import plotly.express as px


class GwasData:

    def __init__(self,
                 phecode,
                 connection):
        """
        :param phecode: phecode of interest
        :param connection: sqlalchemy connection (should be imported)
        """
        self.phecode = phecode

        self.connection = connection
        self.mh_query = f"""SELECT v.*, g.MAF, g.EFFECTSIZE, g.SE, g.LOG10P
                            FROM private_dash.TM90K_LOGP_gt2 g 
                            INNER JOIN private_dash.TM90K_variants v
                            USING(VAR_ID)
                            WHERE PHECODE = '{self.phecode}'"""
        # Dataframe setup operations
        self.data = pd.read_sql(self.mh_query, self.connection).sort_values(['CHR', 'POS']).reset_index(
            drop=True).reset_index().rename(columns={'index': 'REL_POS'})
        self.data['EFFECTSIZE(SE)'] = round(self.data.EFFECTSIZE, 2).astype(str) + '(' + round(self.data.SE, 3).astype(
            str) + ')'

        # Top Results Table
        self.top_results = self.data.query('LOG10P > 5').loc[:,
                           ['VAR_ID', 'GENE', 'IMPACT', 'EFFECT', 'HGVS_c', 'HGVS_p', 'MAF', 'LOG10P',
                            'EFFECTSIZE(SE)']]
        self.top_results['P-value'] = 10 ** -self.top_results['LOG10P']
        self.top_results.rename(columns={'EFFECTSIZE(SE)': 'EffectSize(SE)', 'GENE': 'Gene', 'VAR_ID': 'VarID'},
                                inplace=True)
        self.top_results = self.top_results[
            ['VarID', 'Gene', 'IMPACT', 'EFFECT', 'HGVS_c', 'HGVS_p', 'MAF', 'P-value', 'EffectSize(SE)']].sort_values(
            'P-value').reset_index(drop=True)

        # Manhattan plot information
        self.nChr = len(np.unique(self.data['CHR']))
        self.colors = ['#3498DB', '#3445DB']
        self.plt_ticks = self.data.groupby('CHR').median().loc[:, 'REL_POS'].to_numpy()
        self.hovertemplate = '<br>'.join([
            'VAR_ID: %{customdata[0]}',
            'LOG10P: %{y:.2f}',
            'Beta: %{customdata[5]}',
            'Gene: %{customdata[1]}',
            'Impact: %{customdata[2]}',
            'Effect: %{customdata[3]}'
        ])
        self.custom_data = ['VAR_ID', 'GENE', 'IMPACT', 'EFFECT', 'MAF', 'EFFECTSIZE(SE)']

    def manhattan_plot(self, genomewide_val=5e-8):
        fig = px.scatter(self.data, 'REL_POS', 'LOG10P', color=self.data.CHR.astype(str),
                         color_discrete_sequence=self.colors,
                         custom_data=self.custom_data)
        fig.update_xaxes(title='Chromosome', tickvals=self.plt_ticks,
                         ticktext=np.array(range(1, self.nChr + 1)).astype(str),
                         tickangle=0)
        fig.update_traces(hovertemplate=self.hovertemplate)
        fig.add_shape(type='line',
                      x0=0,
                      x1=self.data['REL_POS'].max(),
                      y0=-np.log10(genomewide_val),
                      y1=-np.log10(genomewide_val),
                      line=dict(color='LightSeaGreen', width=2, dash='dot'))
        fig.update_layout(showlegend=False)
        return fig

    def pheno_info(self):
        df = pd.read_sql(f"""SELECT phenotype, PHECODE, cases, controls, category
                                         FROM private_dash.TM90K_phenotypes 
                                         WHERE PHECODE = '{self.phecode}'""",
                                     self.connection)
        test = df.to_dict('records')[0]
        test['phenotype'] = test['phenotype'].title()
        test['PHECODE'] = test['PHECODE'].replace('_', '.')
        test['category'] = test['category'].title()
        return test
