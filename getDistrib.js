var apiUrl = "http://ec2-52-201-254-121.compute-1.amazonaws.com:5000/distribution"

function displayDist(response)  {
    var categories = []
    for (status in response)    {
        var entry = [status, response[status]]
        categories.push(entry)
    }
    categories.sort(function(a, b)  {
        var massA = a[1]
        var massB = b[1]
        if (massA < massB)
            return -1
        if (massA > massB)
            return 1
        return 0
    })
    categories.reverse()

    for (var i=0; i<categories.length; i++)    {
        var div = document.createElement('div');
        var p = document.createElement('p')
        p.className = "status"
        var statusText = document.createTextNode(categories[i][0]);
        p.appendChild(statusText)
        div.appendChild(p)
                
        var probP = document.createElement('p')
        probP.className = "prob"
        statusText = document.createTextNode(categories[i][1])
        probP.appendChild(statusText)
        div.appendChild(probP)
        document.body.appendChild(div)
    }
}

http.get({url: apiUrl,
          contentType: 'application/json',
          onload: function() {
              var resp = JSON.parse(this.responseText)
              displayDist(resp)
            }
});
