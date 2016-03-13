var apiUrl = "http://nothing-to-see-here/distribution"

function displayDist(response)  {
    var categories = []
    // iterate through key-value pairs in API response
    // and store them in an array data structure
    for (status in response)    {
        var entry = [status, response[status]]
        categories.push(entry)
    }
    // sort categories by their retweet count
    categories.sort(function(a, b)  {
        var massA = a[1]
        var massB = b[1]
        if (massA < massB)
            return -1
        if (massA > massB)
            return 1
        return 0
    })
    // reverse so that most retweeted category is first
    categories.reverse()

    // create HTML DOM elements to display each category in this distribution
    for (var i=0; i<categories.length; i++)    {
        var div = document.createElement('div');
        // display the text of the original @nytimes status
        var p = document.createElement('p')
        p.className = "status"
        var statusText = document.createTextNode(categories[i][0]);
        p.appendChild(statusText)
        div.appendChild(p)
        // display the retweet count of the original @nytimes status 
        var probP = document.createElement('p')
        probP.className = "prob"
        statusText = document.createTextNode(categories[i][1])
        probP.appendChild(statusText)
        div.appendChild(probP)
        document.body.appendChild(div)
    }
}

// make GET request to API endpoint: /distribution
// Credit: https://github.com/wylst/http.js
http.get({url: apiUrl,
          contentType: 'application/json',
          onload: function() {
              var resp = JSON.parse(this.responseText)
              displayDist(resp)
            }
});
