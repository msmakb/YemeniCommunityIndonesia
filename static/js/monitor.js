function loadMemberFormCanvas() {
    let ctx = document.getElementById('member-forms-chart');
    let labels = ctx.getAttribute('data-labels').split(', ');
    let data = ctx.getAttribute('data-data').split(', ');
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                label: 'عدد النماذج المقدمة',
                data: data,
                borderWidth: 1
            }],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function loadFirstVisitCanvas() {
    let ctx = document.getElementById('first-visit-chart');
    let labels = ctx.getAttribute('data-labels').split(', ');
    let data = ctx.getAttribute('data-data').split(', ');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'عدد الزيارات لأول مرة',
                data: data,
                borderWidth: 1
            }],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', loadMemberFormCanvas);
document.addEventListener('DOMContentLoaded', loadFirstVisitCanvas);