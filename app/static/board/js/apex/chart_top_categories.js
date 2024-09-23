// neste tipo de gráfico, é feita uma request a um endpoint para resgatar os dados

document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = getCookie('csrftoken');

    // Resgatar ano e mês do formulário
    const month = document.querySelector("input[name='m']").value;
    const year = document.querySelector("input[name='y']").value;

    // Definindo o payload
    const payload = {
        month: month,
        year: year
    };

    // Fazendo a requisição para obter os dados do back-end
    fetch('charts/top_categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken  // Se necessário para CSRF
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (data.length == 0) {
                document.getElementById('top_categories').innerHTML = '<p style="text-align: center;">Não existem dados suficientes para exibir o gráfico.</p>';
                return
            }

            // Extraindo as categorias, valores, metas e médias dos dados recebidos
            const categories = data.map(item => item.category);
            const amounts = data.map(item => item.amount);
            const goals = data.map(item => item.goal);
            const avgLast3Months = data.map(item => item.avgLast3Months);

            // Configuração do gráfico
            var options = {
                chart: {
                    height: 350,
                    type: 'line',
                    stacked: false,
                    toolbar: {
                        show: false
                    }
                },
                stroke: {
                    width: [0, 2, 4],
                    curve: "smooth"
                },
                plotOptions: {
                    bar: {
                        columnWidth: "50%"
                    }
                },
                colors: ["#f46a6a", "#556ee6", "#34c38f"],  // Vermelho para gastos, azul para metas, verde para médias
                series: [{
                    name: "Gastos",
                    type: "column",
                    data: amounts
                }, {
                    name: "Meta",
                    type: "area",
                    data: goals,
                    fill: {
                        type: 'gradient',
                        gradient: {
                            shade: 'light',
                            type: "vertical",
                            shadeIntensity: 0.25,
                            gradientToColors: undefined, // Cor padrão
                            inverseColors: false,
                            opacityFrom: 0.85,
                            opacityTo: 0.55,
                            stops: [0, 100]
                        }
                    }
                }, {
                    name: "Média Trimestral",
                    type: "line",
                    data: avgLast3Months
                }],
                xaxis: {
                    categories: categories
                },
                yaxis: {
                    title: {
                        text: 'Valor em R$'
                    }
                },
                tooltip: {
                    shared: true,
                    intersect: false,
                    y: {
                        formatter: function (val) {
                            return "R$ " + val;
                        }
                    }
                },
                grid: {
                    borderColor: "#f1f1f1"
                }
            }

            // Renderizando o gráfico
            var chart = new ApexCharts(document.querySelector("#top_categories"), options);
            chart.render();
        })
        .catch(error => console.error('Erro ao carregar os dados:', error));
});