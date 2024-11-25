function titleCase(str) {
   
    var splitStr = str.split("_").join(" ").toLowerCase().split(' ');
    for (var i = 0; i < splitStr.length; i++) {
        // You do not need to check if i is larger than splitStr length, as your for does that for you
        // Assign it back to the array
        splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);     
    }
    // Directly return the joined string
    return splitStr.join(' '); 
}

function firstClick(){
    setTimeout(function(){
        $(".selectpicker").each(function(){
            console.log($(this).parent());
            $(this).next().click();
            $("body").click();
        });
    }, 100);

}

const CHART_COLORS = {
    ubu: 'rgb(170,34,60)',
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};
const weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

const dSplit = [60, 80, 100];
const lSplit = ['OK', 'Warning', 'Danger'];
const cSplit = ['green', 'orange', 'red']

const configBaseBarChart = {
    type: "bar",
    data: {
        datasets: [{
            backgroundColor: CHART_COLORS.ubu,
            borderColor: CHART_COLORS.ubu,
            hoverBackgroundColor: CHART_COLORS.ubu,
            hoverBorderColor: CHART_COLORS.ubu,
            barPercentage: .75,
            categoryPercentage: .5,
        }]
    },
    options: {
        responsive: !window.MSInputMethodContext,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: {
                    display: false
                },
            },
            y: {
                type: 'linear',
                position: 'left',
                grid: {
                    display: true
                }
            }
        }
    }
}

const configBaseGauge = {
    type: 'gauge',
    data: {
        labels: lSplit,
        datasets: [{
            data: dSplit,
            backgroundColor: cSplit,
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        title: {
            display: false,

        },
        needle: {
            radiusPercentage: 2,
            widthPercentage: 3.2,
            lengthPercentage: 80,
            color: 'rgba(0, 0, 0, 1)'
        },
        valueLabel: {
            display: true
        },
        plugins: {
            datalabels: {
                display: false,
                formatter: function (value, context) {
                    return context.chart.data.labels[context.dataIndex];
                },
                color: 'rgba(255, 255, 255, 1.0)',
                backgroundColor: null,
                font: {
                    size: 11,
                    weight: 'bold'
                }
            }
        }
    }
};