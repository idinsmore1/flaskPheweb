$(document).ready(function(){
    // Sonstructs the suggestion engine
    var countries = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // The url points to a json file that contains an array of country names
        prefetch: "{{ url_for('static', filename='data/phenotypes.json') }}"
    });
    
    // Initializing the typeahead with remote dataset
    $('.typeahead').typeahead(null, {
        name: 'countries',
        source: countries,
        limit: 10 /* Specify maximum number of suggestions to be displayed */
    });
});  