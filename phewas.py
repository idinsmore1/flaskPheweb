import pandas as pd
import numpy as np
import plotly.express as px
from itertools import cycle


class PhewasData:

    def __init__(self, variant, connection):
        """
        :param variant: Variant of Interest (VarID format)
        :param connection: database connection (MySQLdb preferred)
        """
        self.variant = variant
        self.variant_info = pd.read_sql(f"SELECT * FROM private_dash.TM90K_variants WHERE VAR_ID = '{variant}'",
                                        connection).to_dict('records').pop()
        self.phewas_query = f"""SELECT g.VAR_ID, 
                                       g.PHECODE,
                                       g.MAF,
                                       g.EFFECTSIZE,
                                       g.LOG10P,
                                       p.cases,
                                       p.controls,
                                       p.phenotype,
                                       p.sex,
                                       p.category as phenoGroup
                                FROM private_dash.TM90K_gwas g
                                    INNER JOIN private_dash.TM90K_phenotypes p
                                        USING(PHECODE)
                                WHERE g.VAR_ID = '{self.variant}'"""
        self.data = pd.read_sql(self.phewas_query, connection)
        self.data['Pvalue'] = 10 ** -self.data.LOG10P
        self.data['phenoGroup'] = self.data['phenoGroup'].fillna('injuries & poisoning')

        self.top_results = self.data.sort_values(['LOG10P'], ascending=False)

    # Function to create the 'manhattan' plot for the Phewas
    def phewas_plot(self):
        phenos = self.data

        # Set the phenotype category to be a categorical variable
        categories = ['infectious diseases',
                      'neoplasms',
                      'endocrine/metabolic',
                      'hematopoietic',
                      'mental disorders',
                      'neurological',
                      'symptoms',
                      'sense organs',
                      'circulatory system',
                      'respiratory',
                      'digestive',
                      'genitourinary',
                      'injuries & poisonings',
                      'pregnancy complications',
                      'dermatologic',
                      'musculoskeletal',
                      'congenital anomalies']
        pheno_cat = pd.CategoricalDtype(categories, ordered=True)
        phenos.phenoGroup = phenos.phenoGroup.astype(pheno_cat)
        phenos['phenoGroup'] = phenos['phenoGroup'].fillna('injuries & poisonings')

        # Sort and group by phenotype group
        grouped = phenos.sort_values(['phenoGroup', 'PHECODE']).reset_index(drop=True)

        # Create the symbols needed to represent effectsize direction
        conditions = [
            (grouped.Pvalue > 0.05),
            (grouped.Pvalue < 0.05) & (grouped.EFFECTSIZE > 0),
            (grouped.Pvalue < 0.05) & (grouped.EFFECTSIZE < 0)
        ]
        values = [1, 2, 3]
        grouped = grouped.reset_index().rename(columns={'index': 'RELPOS'})
        grouped['MarkerGroup'] = np.select(conditions, values)
        symbols = {1: 'circle', 2: 'triangle-up', 3: 'triangle-down'}
        grouped['symbol'] = [symbols[x.MarkerGroup] for x in grouped.itertuples(index=False)]

        # Create labels that match the plot colors
        plot_colors = ['#1F77B4',
                       '#FF7F0E',
                       '#2CA02C',
                       '#D62728',
                       '#9467BD',
                       '#8C564B',
                       '#E377C2',
                       '#7F7F7F',
                       '#BCBD22',
                       '#17BECF']

        # Function to give the x-axis text color matching its group
        def color_string(color, text):
            # color: hexadecimal
            s = "<span style='color:" + str(color) + "'>" + str(text) + "</span>"
            return s

        # Set up the extraneous information for the phewas plot
        x_vals = [x.RELPOS for x in grouped.itertuples(index=False) if any(x.LOG10P >= grouped.LOG10P.nlargest(3))]
        y_vals = [y.LOG10P for y in grouped.itertuples(index=False) if any(y.LOG10P >= grouped.LOG10P.nlargest(3))]
        text = [x.phenotype for x in grouped.itertuples(index=False) if any(x.LOG10P >= grouped.LOG10P.nlargest(3))]
        keys = dict(zip(categories, cycle(plot_colors)))
        plt_ticks = grouped.loc[:, ['phenoGroup', 'RELPOS']].groupby('phenoGroup').min().RELPOS.to_numpy()
        ticktext = [color_string(v, k) for k, v in keys.items()]

        # Set the order that the symbols appear in so that they match on the plot
        symbols = grouped.symbol.unique().tolist()
        custom_data = ['phenotype', 'phenoGroup', 'EFFECTSIZE']
        hovertemplate = '<br>'.join([
            'Phenotype: %{customdata[0]}',
            'Category: %{customdata[1]}',
            'Beta: %{customdata[2]}',
            '-log10(p-value): %{y:.2f}',
            '<extra></extra>'
        ])
        # Create the plot
        fig = px.scatter(grouped, 'RELPOS', 'LOG10P',
                         color='phenoGroup',
                         color_discrete_sequence=plot_colors,
                         symbol=grouped.MarkerGroup,
                         symbol_sequence=symbols,
                         custom_data=custom_data)

        fig.update_traces(marker=dict(size=10, opacity=0.9, line=dict(width=1, color='Black')))
        fig.update_traces(hovertemplate=hovertemplate)
        fig.update_layout(showlegend=False)
        for x, y, text in zip(x_vals, y_vals, text):
            fig.add_annotation(x=x, y=y, text=text, showarrow=False, yshift=10)
        fig.update_xaxes(title='Phenotype', tickvals=plt_ticks, ticktext=ticktext, tickangle=50)
        return fig
