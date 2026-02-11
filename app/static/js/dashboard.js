fetch('/chart-data')
.then(res=>res.json())
.then(data=>{
    new Chart(document.getElementById('chart'),{
        type:'line',
        data:{
            labels:data.labels,
            datasets:[
                {label:'Income',data:data.income},
                {label:'Expense',data:data.expense}
            ]
        }
    })
})

