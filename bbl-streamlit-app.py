import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, datetime

@st.cache
def load_data():
    df = pd.read_csv('seitenliste-neu.csv', sep=",")
    df.id = df.id.astype(str)
    df['ausgabe'] = df['id'].apply(lambda x: datetime.strptime(x[:8], '%Y%m%d'))
    df['url'] = df['id'].apply(lambda x: 'http://digital.slub-dresden.de/id39946221X-'+x)
    #df['titelblatt'] = df['id'].apply(lambda x: f'https://digital.slub-dresden.de/data/kitodo/Brsfded_39946221X-{x}/Brsfded_39946221X-{x}_tif/jpegs/00000001.tif.original.jpg')
    df = df.drop(['id'], axis=1)
    df = df.set_index('ausgabe')
    return df


df = load_data()

st.title('Börsenblatt Explorer')

st.markdown('Das *Börsenblatt für den Deutschen Buchhandel* erscheint seit 1834. Es dokumentiert auf einmalige Weise die Entwicklung des Buchhandels im deutschsprachigen Raum bis zum zweiten Weltkrieg. Die Hefte liegen digitalisiert bei der [Sächsischen Landes- und Universitätsbibliothek (SLUB)](#https://www.slub-dresden.de/) in Dresden vor.')

st.write('Der Börsenblatt Explorer erlaubt eine Sichtung des Gesamtbestandes nach dem _Umfang_ der einzelnen Hefte. Der Umfang wird in einem Diagramm hergestellt. Ein Klick in das Diagram führt zum Digitalisat des Heftes. Auffällig dicke Hefte enthalten etwa Jahresverzeichnisse, erscheinen zur Buchmesse oder sind mit besonders umfangreichen Anzeigenteilen ausgestattet.')



start = date(1834,1,1)
ende = date(1945,12,31)

st.sidebar.header('Auswertungszeitraum')
jahrgang = st.sidebar.slider('', 1834, 1945, [start.year, ende.year])

st.sidebar.header('Auswertungszeitraum taggenau')
heft = st.sidebar.date_input('Ausgaben taggenau wählen', [date.fromisoformat(f'{jahrgang[0]}-01-01'),date.fromisoformat(f'{jahrgang[1]}-12-31')], date.fromisoformat('1834-01-01'), date.fromisoformat('1945-03-17'))


source = df.loc[heft[0]:heft[1]].reset_index()

bar = alt.Chart(source).mark_bar().encode(
    alt.X('ausgabe:T', title='Ausgabe'),
    alt.Y('seiten:Q', title='Seiten, Durchschnitt'),
    tooltip=['ausgabe', 'seiten'],
    href='url:N',
).interactive()

rule = alt.Chart(source).mark_rule(color='red').encode(
    y='mean(seiten):Q'
)

(bar + rule).properties(width=800)
st.header('Umfang pro Ausgabe')
st.altair_chart(bar + rule, use_container_width=True)

st.sidebar.write(df.loc[heft[0]:heft[1]].shape[0], ' Ausgaben mit ', df['seiten'].loc[heft[0]:heft[1]].sum() ,' Seiten im Suchzeitraum')
st.sidebar.write('durchschnittlich ', round(df['seiten'].loc[heft[0]:heft[1]].mean(), 1), 'Seiten pro Ausgabe im Suchzeitraum')

st.header('Ausgaben mit den meisten Seiten')
top = st.slider('Zeige die top x', 5, 100, 10)
st.table(source.nlargest(top, 'seiten', keep='all'))

#for row in source.nlargest(top, 'seiten', keep='all').itertuples(index = True, name ='Pandas'):
#    st.image(getattr(row, "titelblatt"), caption=getattr(row, "url"), width=200)