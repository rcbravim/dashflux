// neste tipo de gráfico, ap invés de fazer um request a um endpoint para resgatar os dados, como em "top_categories",
// os dados são fornecidos via HTML

document.addEventListener("DOMContentLoaded", function () {

    // Extraindo dados do contexto
    var envelopeEntries = envelope_entries;

    // Verifique se 'envelopeEntries' está definido e é uma lista
    if (Array.isArray(envelopeEntries)) {
        var goals = envelopeEntries.map(entry => entry.env_goal);
        var amounts_left = envelopeEntries.map(entry => entry.env_amount_left);
        var envelope_name = envelopeEntries.map(entry => entry.env_name);

        // Calculando o valor gasto em cada envelope
        var amounts_spent = goals.map(function(goal, index) {
            return goal - amounts_left[index];
        });

    } else {
        // Caso não esteja definido, inicialize com arrays vazios
        var goals = [];
        var amounts_left = [];
        var amounts_spent = [];
        var envelope_name = [];
    }

    // Calculando o valor máximo para o eixo Y
    var maxGoal = Math.max(...goals);

    // Configuração do gráfico
    var options = {
        chart: {
            height: 350,
            type: 'bar',
            stacked: true,  // Habilita as barras empilhadas
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: false, // Barras verticais
                columnWidth: "50%",
                dataLabels: {
                  position: 'top',
                }
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function (val, opts) {
                // Exibir o rótulo somente para a série "Restante"
                if (opts.seriesIndex === 1) { // Index 1 é "Restante"
                    return 'R$ ' + val.toFixed(2);
                } else {
                    return '';
                }
            },
            style: {
                fontSize: '12px',
                colors: ["#000000"],  // Cor preta para os rótulos
                fontWeight: 'bold'
            },
            position: 'top',
            offsetY: -25
        },
        colors: ["#f46a6a", "#34c38f"],  // Vermelho para gasto, verde para restante
        series: [{
            name: "Gasto",
            data: amounts_spent
        }, {
            name: "Restante",
            data: amounts_left
        }],
        xaxis: {
            categories: envelope_name,
            labels: {
                style: {
                    colors: "#000000",  // Preto para rótulos do eixo X
                    fontSize: '12px'
                }
            }
        },
        yaxis: {
            show: false,
            title: {
                text: 'Valor em R$',
                style: {
                    color: "#000000",  // Preto para o título do eixo Y
                    fontSize: '14px',
                    fontWeight: 'bold'
                }
            },
            max: maxGoal,
            labels: {
                formatter: function (val) {
                    return 'R$ ' + val.toFixed(2);
                },
                style: {
                    colors: "#000000",  // Preto para rótulos do eixo Y
                    fontSize: '12px'
                }
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return "R$ " + val.toFixed(2);
                }
            }
        },
        grid: {
            borderColor: "#f1f1f1"
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center',
//            offsetX: 40,
            labels: {
                colors: "#000000",  // Preto para rótulos da legenda
            }
        },
    };

    // Renderizando o gráfico
    var chart = new ApexCharts(document.querySelector("#chart_bar_vert"), options);
    chart.render();
});
