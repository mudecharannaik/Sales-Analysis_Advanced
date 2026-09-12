/* Charts + data binding for dashboard.html and report.html.
 * Data source: window.REPORT_DATA (embedded by html_report.py) or data.json fallback. */
(function () {
    'use strict';

    var PALETTE = ['#0d6efd', '#198754', '#ffc107', '#0dcaf0', '#dc3545',
                   '#6f42c1', '#fd7e14', '#20c997', '#6610f2', '#d63384'];

    function fmtMoney(v) {
        return '$' + Number(v || 0).toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
    function fmtNum(v) {
        return Number(v || 0).toLocaleString('en-US');
    }
    function esc(v) {
        return v == null ? '' : String(v)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function loadData() {
        if (window.REPORT_DATA && Object.keys(window.REPORT_DATA).length) {
            return Promise.resolve(window.REPORT_DATA);
        }
        return fetch('data.json').then(function (r) {
            if (!r.ok) throw new Error('data.json HTTP ' + r.status);
            return r.json();
        });
    }

    function makeChart(canvasId, config) {
        var el = document.getElementById(canvasId);
        if (!el || typeof Chart === 'undefined') return null;
        return new Chart(el.getContext('2d'), config);
    }

    function lineConfig(labels, datasets) {
        return {
            type: 'line',
            data: { labels: labels, datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: { y: { beginAtZero: true } }
            }
        };
    }

    function barConfig(labels, values, label) {
        return {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    backgroundColor: PALETTE,
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        };
    }

    /* ===================== DASHBOARD PAGE ===================== */
    function renderDashboard(d) {
        var kpis = d.kpis || {};
        var map = {
            'kpi-sales': kpis.total_sales != null ? fmtMoney(kpis.total_sales) : '--',
            'kpi-profit': kpis.total_profit != null ? fmtMoney(kpis.total_profit) : '--',
            'kpi-orders': kpis.orders != null ? fmtNum(kpis.orders) : '--',
            'kpi-customers': kpis.customers != null ? fmtNum(kpis.customers) : '--'
        };
        Object.keys(map).forEach(function (id) {
            var el = document.getElementById(id);
            if (el) el.textContent = map[id];
        });

        var monthly = d.monthly || [];
        var labels = monthly.map(function (r) { return r.label; });

        makeChart('salesTrendChart', lineConfig(labels, [
            {
                label: 'Sales', data: monthly.map(function (r) { return r.sales; }),
                borderColor: PALETTE[0], backgroundColor: 'rgba(13,110,253,0.15)',
                tension: 0.3, fill: true
            },
            {
                label: 'Profit', data: monthly.map(function (r) { return r.profit; }),
                borderColor: PALETTE[1], backgroundColor: 'rgba(25,135,84,0.15)',
                tension: 0.3, fill: true
            }
        ]));

        var cat = d.category || [];
        makeChart('categoryChart', {
            type: 'doughnut',
            data: {
                labels: cat.map(function (r) { return r.label; }),
                datasets: [{ data: cat.map(function (r) { return r.sales; }), backgroundColor: PALETTE }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });

        var mkt = d.market || [];
        makeChart('marketChart', barConfig(
            mkt.map(function (r) { return r.label; }),
            mkt.map(function (r) { return r.sales; }), 'Sales'));

        makeChart('scatterChart', {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Order (Sales vs Profit)',
                    data: d.scatter || [],
                    backgroundColor: 'rgba(13,110,253,0.55)'
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { title: { display: true, text: 'Sales' }, beginAtZero: true },
                    y: { title: { display: true, text: 'Profit' } }
                }
            }
        });

        renderDataTable(d.rows || []);
    }

    function renderDataTable(rows) {
        var tbody = document.querySelector('#dataTable tbody');
        if (!tbody) return;
        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">No data available.</td></tr>';
            return;
        }
        drawRows(rows);

        var input = document.getElementById('searchInput');
        if (input) {
            input.addEventListener('keyup', function () {
                var q = input.value.toLowerCase();
                drawRows(rows.filter(function (r) {
                    return Object.keys(r).some(function (k) {
                        return String(r[k]).toLowerCase().indexOf(q) !== -1;
                    });
                }));
            });
        }

        function drawRows(data) {
            if (!data.length) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">No matching records.</td></tr>';
                return;
            }
            tbody.innerHTML = data.slice(0, 500).map(function (r) {
                return '<tr>' +
                    '<td>' + esc(r.order_id) + '</td>' +
                    '<td>' + esc(r.date) + '</td>' +
                    '<td>' + esc(r.customer) + '</td>' +
                    '<td>' + esc(r.category) + '</td>' +
                    '<td class="text-end">' + fmtMoney(r.sales) + '</td>' +
                    '<td class="text-end">' + fmtMoney(r.profit) + '</td>' +
                    '<td>' + esc(r.region) + '</td></tr>';
            }).join('');
        }
    }

    function renderReport(d) {
        var kpis = d.kpis || {};
        setText('summary-records', kpis.records != null ? fmtNum(kpis.records) : '--');
        setText('summary-sales', kpis.total_sales != null ? fmtMoney(kpis.total_sales) : '--');
        setText('summary-profit', kpis.total_profit != null ? fmtMoney(kpis.total_profit) : '--');
        setText('summary-margin', kpis.margin != null ? kpis.margin + '%' : '--');

        var q = d.quality;
        if (q) {
            setHtml('quality-content',
                '<div class="row g-3">' +
                '<div class="col-md-4"><strong>Quality Score:</strong> ' + (q.score != null ? q.score + '%' : 'n/a') + '</div>' +
                '<div class="col-md-4"><strong>Missing Cells:</strong> ' + fmtNum(q.missing_cells || 0) + '</div>' +
                '<div class="col-md-4"><strong>Duplicate Rows:</strong> ' + fmtNum(q.duplicate_rows || 0) + '</div>' +
                '</div>');
        }

        if (d.statistical_tests && d.statistical_tests.length) {
            var rowsHtml = d.statistical_tests.map(function (t) {
                return '<tr><td>' + esc(t.name) + '</td><td>' + esc(t.statistic) +
                    '</td><td>' + esc(t.p_value) + '</td><td>' + esc(t.conclusion) + '</td></tr>';
            }).join('');
            setHtml('statistical-content',
                '<table class="table table-sm"><thead class="table-light"><tr>' +
                '<th>Test</th><th>Statistic</th><th>p-value</th><th>Conclusion</th>' +
                '</tr></thead><tbody>' + rowsHtml + '</tbody></table>');
        }

        var rc = d.repeat_customers;
        if (rc) {
            setHtml('repeat-content',
                '<ul class="list-unstyled mb-0">' +
                '<li><strong>Total Customers:</strong> ' + fmtNum(rc.total_customers) + '</li>' +
                '<li><strong>Repeat Customers:</strong> ' + fmtNum(rc.repeat_customers) + '</li>' +
                '<li><strong>Repeat Rate:</strong> ' + (rc.repeat_rate != null ? rc.repeat_rate + '%' : '--') + '</li>' +
                '<li><strong>Avg Orders / Customer:</strong> ' + (rc.avg_orders != null ? rc.avg_orders : '--') + '</li>' +
                '</ul>');
        }

        var seg = d.segments || {};
        var segLabels = Object.keys(seg);
        if (segLabels.length) {
            makeChart('rfmChart', barConfig(segLabels, segLabels.map(function (k) { return seg[k]; }), 'Customers'));
        }

        var par = d.pareto || [];
        if (par.length) {
            makeChart('paretoChart', {
                type: 'bar',
                data: {
                    labels: par.map(function (r) { return r.label; }),
                    datasets: [
                        { label: 'Sales', data: par.map(function (r) { return r.sales; }), backgroundColor: PALETTE[0], yAxisID: 'y' },
                        { label: 'Cumulative %', data: par.map(function (r) { return r.cum_pct; }), type: 'line', borderColor: PALETTE[2], backgroundColor: PALETTE[2], yAxisID: 'y1', tension: 0.3 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Sales' } },
                        y1: { position: 'right', min: 0, max: 100, grid: { drawOnChartArea: false }, title: { display: true, text: 'Cumulative %' } }
                    }
                }
            });
        }

        var geo = d.geo || [];
        if (geo.length) {
            makeChart('geoChart', barConfig(
                geo.map(function (r) { return r.label; }),
                geo.map(function (r) { return r.sales; }), 'Sales'));
        }

        var trend = d.ts_trend || [];
        if (trend.length) {
            makeChart('tsTrendChart', lineConfig(
                trend.map(function (r) { return r.label; }),
                [{ label: 'Sales', data: trend.map(function (r) { return r.sales; }), borderColor: PALETTE[0], backgroundColor: 'rgba(13,110,253,0.15)', tension: 0.3, fill: true }]));
        }

        var fc = d.ts_forecast || [];
        if (fc.length) {
            makeChart('tsForecastChart', lineConfig(
                fc.map(function (r) { return r.label; }),
                [
                    { label: 'Actual', data: fc.map(function (r) { return r.actual; }), borderColor: PALETTE[0], tension: 0.3 },
                    { label: 'Forecast', data: fc.map(function (r) { return r.forecast; }), borderColor: PALETTE[2], borderDash: [6, 4], tension: 0.3 }
                ]));
        }

        var fi = d.feature_importance || [];
        if (fi.length) {
            makeChart('featureChart', barConfig(
                fi.map(function (r) { return r.label; }),
                fi.map(function (r) { return r.value; }), 'Importance'));
        }

        var ap = d.actual_vs_predicted || [];
        if (ap.length) {
            var maxV = Math.max.apply(null, ap.map(function (r) { return r.actual; }));
            makeChart('actualPredChart', {
                type: 'scatter',
                data: {
                    datasets: [
                        { label: 'Samples', data: ap.map(function (r) { return { x: r.actual, y: r.predicted }; }), backgroundColor: 'rgba(13,110,253,0.55)' },
                        { label: 'Ideal (y = x)', type: 'line', data: [{ x: 0, y: 0 }, { x: maxV, y: maxV }], borderColor: PALETTE[4], pointRadius: 0, fill: false }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    scales: { x: { title: { display: true, text: 'Actual' } }, y: { title: { display: true, text: 'Predicted' } } }
                }
            });
        }

        document.querySelectorAll('.placeholder-img[data-viz]').forEach(function (img) {
            img.src = '../../Visualizations/' + img.getAttribute('data-viz');
        });

        function setText(id, val) {
            var el = document.getElementById(id);
            if (el) el.textContent = val;
        }
        function setHtml(id, val) {
            var el = document.getElementById(id);
            if (el) el.innerHTML = val;
        }
    }

    /* ===================== BOOTSTRAP ===================== */
    function imgFallback() {
        document.querySelectorAll('.placeholder-img').forEach(function (img) {
            if (img.getAttribute('src') === '#') img.style.display = 'none';
            img.addEventListener('error', function () { img.style.display = 'none'; });
        });
    }

    function exportDashboard() {
        var blob = new Blob([JSON.stringify(window.REPORT_DATA || {}, null, 2)],
            { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'dashboard_data.json';
        a.click();
        URL.revokeObjectURL(a.href);
    }
    window.exportDashboard = exportDashboard;

    loadData()
        .then(function (d) {
            window.REPORT_DATA = d;
            if (document.getElementById('dataTable')) renderDashboard(d);
            if (document.getElementById('summary-records')) renderReport(d);
            imgFallback();
        })
        .catch(function (err) {
            console.error('Failed to load report data:', err);
        });
})();