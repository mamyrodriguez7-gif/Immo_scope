async function loadData() {
    try {
        // --- Charger JSON ---
        const jsonResp = await fetch('data/reports/dashboard_data.json');
        if (!jsonResp.ok) {
            throw new Error(`Erreur chargement JSON (${jsonResp.status})`);
        }
        const dashboardData = await jsonResp.json();

        // --- Charger CSV ---
        const csvResp = await fetch('data/processed/dvf_cleaned.csv');
        if (!csvResp.ok) {
            throw new Error(`Erreur chargement CSV (${csvResp.status})`);
        }
        const csvText = await csvResp.text();

        // --- Parser CSV ---
        const parsed = Papa.parse(csvText, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true
        });

        return { dashboardData, data: parsed.data };

    } catch (e) {
        console.error("❌ Erreur loadData():", e);
        throw e;
    }
}

async function renderCharts() {
    try {
        const { dashboardData, data } = await loadData();

        // ---- Afficher métriques ----
        const metricsDiv = document.getElementById('metrics');
        metricsDiv.innerHTML = `
            <p><strong>Total transactions :</strong> ${dashboardData.metrics.total_transactions}</p>
            <p><strong>Prix moyen :</strong> ${dashboardData.metrics.avg_price_m2} €/m²</p>
        `;

        // ---- Répartition types de biens ----
        const typesCount = {};
        data.forEach(d => {
            if (d.type_local) {
                typesCount[d.type_local] = (typesCount[d.type_local] || 0) + 1;
            }
        });

        Plotly.newPlot('property-types', [{
            values: Object.values(typesCount),
            labels: Object.keys(typesCount),
            type: 'pie',
            textinfo: 'percent+label',
            marker: { colors: ['#FF6B6B', '#4ECDC4', '#FFD166'] }
        }], {
            title: 'Répartition des types de biens',
            title_x: 0.5
        });

        // ---- Distribution des prix ----
        const prixM2 = data.map(d => d.prix_m2).filter(v => !isNaN(v));

        Plotly.newPlot('price-distribution', [{
            x: prixM2,
            type: 'histogram',
            marker: { color: '#45B7D1' }
        }], {
            title: 'Distribution des prix au m² en France',
            title_x: 0.5,
            bargap: 0.05
        });

        // ---- Top communes ----
        const communeCount = {};
        data.forEach(d => {
            if (d.nom_commune) {
                communeCount[d.nom_commune] = (communeCount[d.nom_commune] || 0) + 1;
            }
        });

        const topCommunes = Object
            .entries(communeCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        Plotly.newPlot('top-communes', [{
            x: topCommunes.map(d => d[1]),
            y: topCommunes.map(d => d[0]),
            type: 'bar',
            orientation: 'h',
            marker: {
                color: topCommunes.map(d => d[1]),
                colorscale: 'Viridis'
            },
            text: topCommunes.map(d => d[1]),
            textposition: 'outside'
        }], {
            title: 'Top 10 communes par transactions',
            title_x: 0.5,
            margin: { l: 150 }
        });

        // ---- Surface vs Prix ----
        const validPoints = data.filter(
            d => d.surface_reelle_bati && d.prix_m2 && !isNaN(d.surface_reelle_bati) && !isNaN(d.prix_m2)
        );

        const sample = validPoints.sort(() => 0.5 - Math.random()).slice(0, 300);

        Plotly.newPlot('surface-vs-price', [{
            x: sample.map(d => d.surface_reelle_bati),
            y: sample.map(d => d.prix_m2),
            mode: 'markers',
            type: 'scatter',
            text: sample.map(d => d.nom_commune),
            marker: {
                color: sample.map(d => d.type_local === 'Maison' ? 1 : 2),
                colorscale: ['#FF6B6B', '#4ECDC4'],
                showscale: true
            }
        }], {
            title: 'Surface vs Prix au m²',
            title_x: 0.5,
            xaxis: { title: 'Surface (m²)' },
            yaxis: { title: 'Prix (€)' }
        });

    } catch (e) {
        console.error(" Erreur renderCharts():", e);
    }
}

renderCharts();
