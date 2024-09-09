document.addEventListener("DOMContentLoaded", function () {

    const topCategories = fetchTopCategories();

    // Dados fictícios de categorias, gastos, metas e médias dos últimos 3 meses
    const topCategories = [
        { category: "Alimentação", amount: 1200, goal: 1500, avgLast3Months: 1100 },
        { category: "Transporte", amount: 900, goal: 600, avgLast3Months: 800 },
        { category: "Educação", amount: 850, goal: 800, avgLast3Months: 820 },
        { category: "Lazer", amount: 750, goal: 700, avgLast3Months: 780 },
        { category: "Saúde", amount: 650, goal: 900, avgLast3Months: 670 },
        { category: "Habitação", amount: 600, goal: 1000, avgLast3Months: 620 },
        { category: "Serviços", amount: 550, goal: 500, avgLast3Months: 540 },
        { category: "Vestuário", amount: 500, goal: 450, avgLast3Months: 510 },
        { category: "Tecnologia", amount: 450, goal: 600, avgLast3Months: 460 },
        { category: "Outros", amount: 400, goal: 350, avgLast3Months: 420 }
    ];

    // Extraindo as categorias, valores, metas e médias
    const categories = topCategories.map(item => item.category);
    const amounts = topCategories.map(item => item.amount);
    const goals = topCategories.map(item => item.goal);
    const avgLast3Months = topCategories.map(item => item.avgLast3Months);

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
            name: "Metas",
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
    var chart = new ApexCharts(document.querySelector("#top_categories_backup"), options);
    chart.render();
});
