# Úplně první cvičení po prezentaci
# -------------------------------------
# Otevřít terminál.
# Napsat pip install streamlit 
# Napsat streamlit hello.

# Otevřeme nový soubor app.py a vložíme do něj následující kód:
import streamlit as st
import pandas as pd
import plotly.express as px  
from io import BytesIO
from xhtml2pdf import pisa
import datetime

# --- HLAVIČKA APPKY ---
st.title("Můj první Dashboard 📈")       # nadpis ve streamlit
st.write("Tohle bude moje první aplikace v pythonu")      # text ve streamlit

# --- DATA ---
# Teď řekneme Pythonu, aby si vzal naše CSV
df = pd.read_csv("finalni_data_eshop.csv")        # název CSV souboru
df['OrderDate'] = pd.to_datetime(df['OrderDate']) # Převedeme sloupec s datem na datetime formát

st.header("Kontrola dat")                         # nadpis sekce
st.dataframe(df.head())                           # Zobrazí prvních 5 řádků
# Po každé úpravě je třeba stisknout ctrl + S aby se appka aktualizovala
# a následeně refreshnout v prohlížeči.

# --- 3. ANALÝZA (Nabalujeme kód dál) ---
# Cíl: Spočítat celkový obrat a ukázat ho jako profesionální ukazatel.
st.header("Základní výsledky")              # nadpis sekce

# Výpočet: Sečteme sloupec Celkova_Cena
celkovy_obrat = df['Celkova_Cena'].sum()    # Celkový obrat e-shopu

# Zobrazení: Použijeme speciální prvek pro dashboardy
st.metric(label="Celkový obrat e-shopu", value=f"{celkovy_obrat:,.0f} Kč")   # Zobrazení metriky s formátováním

# Příprava dat pro měsíce
# Cíl: Naučit Python, jak poznat březen od dubna.
# V CSV máme datum jako celý den (např. 2025-03-06). My ale potřebujeme jen měsíc. Přidejte tento blok pod načtení dat:

# --- PŘÍPRAVA MĚSÍCŮ ---
# Vytvoříme si pomocné tabulky pro každý měsíc
df_brezen = df[df['OrderDate'].dt.month == 3]
df_duben = df[df['OrderDate'].dt.month == 4]
df_kveten = df[df['OrderDate'].dt.month == 5]

# Spočítáme si obraty
obr_3 = df_brezen['Celkova_Cena'].sum()
obr_4 = df_duben['Celkova_Cena'].sum()
obr_5 = df_kveten['Celkova_Cena'].sum()

# Rozvržení do sloupců (st.columns)
# Cíl: Dát metriky vedle sebe, ne pod sebe.
#Streamlit standardně sází vše pod sebe. Pokud chceme sloupce, musíme si je „objednat“:

# --- ROZVRŽENÍ ---
st.header("Měsíční vývoj tržeb")

# Vytvoříme 3 sloupce
col1, col2, col3 = st.columns(3)

# Teď budeme psát do každého sloupce zvlášť pomocí "with"
with col1:
    st.metric("Březen", f"{obr_3:,.0f} Kč")

with col2:
    rozdil_4 = obr_4 - obr_3 # O kolik byl duben lepší/horší
    st.metric("Duben", f"{obr_4:,.0f} Kč", delta=f"{rozdil_4:,.0f} Kč")

with col3:
    rozdil_5 = obr_5 - obr_4 # O kolik byl květen lepší/horší
    st.metric("Květen", f"{obr_5:,.0f} Kč", delta=f"{rozdil_5:,.0f} Kč")

# --- PŘÍPRAVA MĚSÍCŮ PRO SIDEBAR ---
# Vytvoříme si pomocné tabulky pro každý měsíc
df_brezen = df[df['OrderDate'].dt.month == 3]
df_duben = df[df['OrderDate'].dt.month == 4]
df_kveten = df[df['OrderDate'].dt.month == 5]

# --- SIDEBAR: NASTAVENÍ ---
st.sidebar.header("Dálkové ovládání")

# 1. Uživatel si vybere slovo
vybrany_mesic = st.sidebar.selectbox(
    "Který měsíc chcete podrobně zkoumat?",
    ["Březen", "Duben", "Květen"]
)

# 2. Překladač: Změníme slovo na číslo (3, 4 nebo 5)
prevodnik = {"Březen": 3, "Duben": 4, "Květen": 5}
mesic_cislo = prevodnik[vybrany_mesic]

# 3. Filtr: Vyřízneme z velké tabulky jen ten správný měsíc
df_filtr = df[df['OrderDate'].dt.month == mesic_cislo]

# --- DETAILNÍ PŘEHLED ---
st.header(f"Detailní výsledky za: {vybrany_mesic}")

col_a, col_b = st.columns(2)

with col_a:
    obrat_mesice = df_filtr['Celkova_Cena'].sum()
    st.metric("Obrat v tomto měsíci", f"{obrat_mesice:,.0f} Kč")

with col_b:
    pocet_obj = len(df_filtr)
    st.metric("Počet objednávek", f"{pocet_obj} ks")
    
# --- TABULKA TOP ZÁKAZNÍKŮ ---
st.subheader(f"TOP 5 nejlepších zákazníků ({vybrany_mesic})")

# 1. Výpočet: Seskupíme podle ID zákazníka a sečteme jeho nákupy
# Používáme naši vyfiltrovanou tabulku 'df_filtr'!
top_zakaznici = df_filtr.groupby('CustomerID')['Celkova_Cena'].sum().nlargest(5)
#groupby('CustomerID'): „Dej na jednu hromadu všechny řádky, které patří stejnému zákazníkovi.“
# ['Celkova_Cena']: „Zajímají mě jen peníze, které u nás nechal.“
# .sum(): „Sečti ty peníze na každé hromadě.“
# .nlargest(5): „Seřaď je od největšího a ukaž mi jen prvních pět.“

# 2. Zobrazení: Jednoduchá tabulka
st.table(top_zakaznici)

# --- GRAF: TREND TRŽEB ---
import plotly.express as px

st.header(f"Graf prodeje v čase ({vybrany_mesic})")

# Nejdřív data trochu "učísneme" - sečteme tržby podle jednotlivých dnů
denni_trzby = df_filtr.groupby('OrderDate')['Celkova_Cena'].sum().reset_index()

# Vytvoříme graf
fig_trend = px.line(
    denni_trzby, 
    x='OrderDate', 
    y='Celkova_Cena',
    title=f"Denní tržby - {vybrany_mesic}",
    markers=True # Přidá tečky na čáru pro lepší čitelnost
)

# Šup s ním na web
st.plotly_chart(fig_trend, use_container_width=True)

st.header("Oblíbenost kategorií")

# Koláčový graf (Pie chart)
fig_pie = px.pie(
    df_filtr, 
    names='kategorie', 
    values='Celkova_Cena',
    hole=0.4 # Udělá z koláče moderní "donut"
)

st.plotly_chart(fig_pie, use_container_width=True)

# --- GRAF: TOP PRODUKTY ---
st.header(f"TOP 10 nejprodávanějších knih ({vybrany_mesic})")

# 1. Příprava dat: Seskupíme podle názvu knihy a sečteme tržby
top_knihy = df_filtr.groupby('nazev_knihy')['Celkova_Cena'].sum().nlargest(10).reset_index()

# 2. Tvorba grafu
fig_produkty = px.bar(
    top_knihy,
    x='Celkova_Cena',
    y='nazev_knihy',
    orientation='h', # Vodorovné sloupce jsou pro názvy knih lepší
    title="Tržby podle knih",
    labels={'Celkova_Cena': 'Celková tržba (Kč)', 'nazev_knihy': 'Kniha'},
    color='Celkova_Cena', # Sloupce budou mít barvu podle výše tržeb
    color_continuous_scale='Viridis' # Hezká barevná paleta
)

# 3. Úprava vzhledu: Aby byly knihy seřazené od největší po nejmenší
fig_produkty.update_layout(yaxis={'categoryorder':'total ascending'})

# 4. Zobrazení
st.plotly_chart(fig_produkty, use_container_width=True)

# --- GENEROVÁNÍ PDF ---

# Instalace v terminálu: pip install fpdf2

from fpdf import FPDF

def generuj_pdf(data_tabulka, nazev_mesice):
    # 1. Inicializace PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 2. Registrace a nastavení českého fontu
    # Soubor 'arial.ttf' MUSÍ být ve stejné složce jako app.py
    pdf.add_font('ArialCZ', '', 'arial.ttf')
    pdf.set_font('ArialCZ', size=16)
    
    # 3. Nadpis (align='C' je na střed)
    pdf.cell(190, 10, txt=f"Měsíční report: {nazev_mesice}", ln=True, align='C')
    
    pdf.set_font('ArialCZ', size=10)
    pdf.cell(190, 10, txt=f"Vygenerováno: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10) # Mezera
    
    # 4. TABULKA (Skládáme ji ručně, aby čeština stoprocentně klapla)
    # Hlavička
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(120, 10, txt="Název knihy", border=1, fill=True)
    pdf.cell(70, 10, txt="Tržba (Kč)", border=1, fill=True)
    pdf.ln()
    
    # Data z tabulky
    pdf.set_fill_color(255, 255, 255)
    for _, row in data_tabulka.iterrows():
        # txt=str(...) zajistí, že se text převede správně
        pdf.cell(120, 10, txt=str(row[0]), border=1)
        pdf.cell(70, 10, txt=f"{row[1]:,.0f} Kč", border=1)
        pdf.ln()
    
    # --- TA NEJDŮLEŽITĚJŠÍ ČÁST PRO STREAMLIT ---
    # pdf.output() vrátí bytearray, my ho musíme přebalit na bytes
    objekt_pdf = pdf.output()
    return bytes(objekt_pdf)

# -- TLAČÍTKO PRO EXPORT PDF ---

st.divider() # Udělá hezkou čáru
st.header("Export reportu")

# 1. Připravíme data pro PDF (vezmeme jen TOP 5 knih)
top_data_pro_pdf = df_filtr.groupby('nazev_knihy')['Celkova_Cena'].sum().nlargest(5).reset_index()

# 2. Vygenerujeme soubor (zatím jen do paměti Pythonu)
pdf_soubor = generuj_pdf(top_data_pro_pdf, vybrany_mesic)

# 3. Zobrazíme tlačítko
st.download_button(
    label="📥 Stáhnout měsíční report v PDF",
    data=pdf_soubor,
    file_name=f"report_{vybrany_mesic}.pdf",
    mime="application/pdf"
)