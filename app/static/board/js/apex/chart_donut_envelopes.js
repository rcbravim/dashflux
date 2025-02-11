// neste tipo de gráfico, ap invés de fazer um request a um endpoint para resgatar os dados, como em "top_categories",
// os dados são fornecidos via HTML

document.addEventListener("DOMContentLoaded", function () {

    // Extraindo dados do contexto
    var envelopeEntries = envelope_entries;

    // Verifique se 'envelopeEntries' está definido e é uma lista
    if (Array.isArray(envelopeEntries)) {
        envelopeEntries.forEach(function(entry, index) {
            var goal = parseFloat(entry.env_goal);
            var amount_left = parseFloat(entry.env_amount_left);
            var envelope_name = entry.env_name;

            // Validar se os valores são números
            if (isNaN(goal) || isNaN(amount_left)) {
                console.error('Valores inválidos para o envelope:', envelope_name);
                return;
            }

            // Calculando o valor gasto para este envelope
            var amount_spent = goal - amount_left;

            // Criando um contêiner para o gráfico
            var chartContainer = document.createElement('div');
            chartContainer.id = 'chart_envelope_' + index;
            chartContainer.style.width = '350px';
            chartContainer.style.display = 'inline-block';
            chartContainer.style.margin = '10px';

            // Adicionando o contêiner ao elemento principal
            document.getElementById('chart_donut').appendChild(chartContainer);

            // Configuração do gráfico donut para este envelope
            var options = {
                chart: {
                    type: 'donut',
                    height: 350,
                },
                series: [amount_spent, amount_left],
                labels: ['Gasto', 'Restante'],
                colors: ["#f46a6a", "#34c38f"],  // Vermelho para gasto, verde para restante
                dataLabels: {
                    enabled: true,
                    formatter: function (val, opts) {
                        var valorReal = opts.w.config.series[opts.seriesIndex];
                        return 'R$ ' + valorReal.toFixed(2);
                    },
                    style: {
                        fontSize: '14px',
                        fontWeight: 'bold',
                        colors: ["#000000"]
                    }
                },
                title: {
                    text: envelope_name,
                    align: 'center',
                    style: {
                        fontSize: '16px',
                        color: '#000000'
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        colors: ["#000000"],  // Preto para rótulos da legenda
                    }
                },
                tooltip: {
                    y: {
                        formatter: function (val) {
                            return "R$ " + val.toFixed(2);
                        }
                    }
                },
            };

            // Renderizando o gráfico para este envelope
            var chart = new ApexCharts(document.querySelector('#' + chartContainer.id), options);
            chart.render();
        });
    } else {
        console.log('Nenhum envelope encontrado.');
    }

});
