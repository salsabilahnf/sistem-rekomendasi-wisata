from flask import Flask, request, make_response, render_template, redirect, url_for
from flask.helpers import url_for
import pandas as pd
import numpy as np

app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template("Home.html")

@app.route("/wisata", methods=["POST"])
def wisata():
    data = pd.read_excel("data/data_wisata.xlsx")
    recommendation = pd.DataFrame(columns=['Destinasi_Wisata',  'Kategori', 'Lokasi', 'Daya_Tarik'])
    count = 0

    for i in data["Destinasi_Wisata"]:
        recommendation.at[count, 'Destinasi_Wisata'] = data["Destinasi_Wisata"].iloc[count]
        recommendation.at[count, 'Lokasi'] = data["Lokasi"].iloc[count]
        recommendation.at[count, 'Daya_Tarik'] = data["Daya_Tarik"].iloc[count]
        recommendation.at[count, 'Kategori'] = data["Kategori"].iloc[count]
        count += 1

    headers = list(enumerate(recommendation.columns, 1))
    rows = []
    for _, row in recommendation.iterrows():
            rows.append(list(enumerate(row, 1)))

    return render_template("Halamanwisata.html", headers=headers, rows=rows)

@app.route("/recommendation", methods=["POST"])
def recommendation():
    if request.method == "POST":
        product_name = str(request.form["product_name"])
        df = rec_jac(product_name)
        df.sort_values(by='Skor_Kemiripan', ascending=False, inplace=True)
        headers = list(enumerate(df.columns, 1))
        rows = []

        for _, row in df.iterrows():
            rows.append(list(enumerate(row, 1)))
        return render_template("Halamanrekomendasi.html", headers=headers, rows=rows)


def rec_jac(title):
    data = pd.read_excel("data/data_wisata.xlsx")
    cosine_sim = pd.read_excel("data/cosine.xlsx")
    jac_sim = pd.read_excel("data/Jaccard.xlsx")
    recommendation = pd.DataFrame(columns=['Destinasi_Wisata', 'Lokasi', 'Daya_Tarik', 'Skor_Kemiripan'])
    count = 0

    titles = data["Destinasi_Wisata"]
    lokasi = data["Lokasi"]
    daya_tarik = data["Daya_Tarik"]
    indices_lokasi = pd.Series(data.index, index=data["Destinasi_Wisata"]).drop_duplicates()

    if title not in indices_lokasi:
        print(f"Error: {title} tidak ditemukan dalam data.")
        return recommendation

    idx = indices_lokasi[title]
    sim_scores_jaccard = jac_sim[idx]
    sim_scores_cosine = cosine_sim[idx]

    # Urutkan indeks berdasarkan skor jaccard secara descending
    sorted_indices_jaccard = np.argsort(sim_scores_jaccard)[::-1]
    # Ambil 5 teratas tanpa objek itu sendiri
    wisata_indices_jaccard = [i for i in sorted_indices_jaccard if i != idx][:5]

    for i in wisata_indices_jaccard:
        recommendation.at[count, 'Destinasi_Wisata'] = titles.iloc[i]
        recommendation.at[count, 'Lokasi'] = lokasi.iloc[i]
        recommendation.at[count, 'Daya_Tarik'] = daya_tarik.iloc[i]
        recommendation.at[count, 'Skor_Kemiripan'] = round(sim_scores_cosine[i], 4) 
        count += 1

    return recommendation

if __name__ == '__main__':
    app.run(debug=True)