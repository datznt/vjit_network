(function ($) {
    function renderCharts(chartData) {
        if (chartData == null || typeof (chartData) != "object") return;
        var { traffic_statistics, user_type_statistics } = chartData.charts;
        new Chart(document.getElementById('chart-1'), {
            type: 'line',
            data: {
                labels: traffic_statistics.labels,
                datasets: traffic_statistics.datasets
            },
            options: {
                title: {
                    display: true,
                    text: 'Statistics graph of user visits'
                }
            }
        });
        console.log(user_type_statistics);
        new Chart(document.getElementById('chart-2'), {
            type: 'doughnut',
            data: {
                labels: user_type_statistics.labels,
                datasets: user_type_statistics.datasets
            },
            options: {
                title: {
                    display: true,
                    text: 'User differential statistical chart'
                }
            }
        });
    }

    function fetchAPI(success, error) {
        $.ajax({
            url: '/dashboard-data'
        }).done(function (data) {
            renderCharts(data);
        })
    }

    $(document).ready(function () { fetchAPI() })
})(django.jQuery);