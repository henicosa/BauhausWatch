document.addEventListener("DOMContentLoaded", generateCommitteeChips);

    function generateCommitteeChips() {
    // Get the timeline element
    var timeline = document.getElementById("timeline");
    // Get the committee chips div
    var committeeChipsDiv = document.getElementById("committee-chips");
    committeeChipsDiv.innerHTML = '';

    var stats = {};
    var categories = ["uni", "media", "engineering", "architecture", "art"];
    translate_category = {
        "uni": "BUW",
        "media": "Medien",
        "engineering": "Bauingenieurwesen",
        "architecture": "Architektur",
        "art": "Kunst"
    }
    // Loop through each protocol element in the timeline
    var protocolElements = timeline.querySelectorAll("[id^='protocol_']");
    protocolElements.forEach(function(protocolElement) {

        // only count if protocol is visible
        if (protocolElement.style.display == 'none') {
            return;
        }

        // Extract data from the protocol element
        var committee = protocolElement.querySelector(".content h2").textContent;
        var matches = protocolElement.querySelectorAll(".content .match-url").length;
        
        // Create chip HTML
        // test if category is present as class
        for (var i = 0; i < categories.length; i++) {
            if (protocolElement.classList.contains(categories[i])) {
                if (stats[categories[i]] == undefined) {
                    stats[categories[i]] = 0;
                }
                stats[categories[i]] += 1;
            }
        }

        // add committee
        if (stats[committee] == undefined) {
            stats[committee] = 0;
        }
        stats[committee] += 1;
    });

    // Fill the committee chips div with the generated HTML based on stats

    // Initialize an empty string to store chip HTML
    var chipHTML = '';

    // Loop through each category in stats sorted by value
    var sorted_categories = Object.keys(stats).sort(function(a, b) {
        return stats[b] - stats[a];
    });

    for (var i = 0; i < sorted_categories.length; i++) {
        var category = sorted_categories[i];
        var value = stats[category];
        var translation = category;
        if (category in translate_category) {
            translation = translate_category[category];
        }
        chipHTML += '<div class="' + category + ' chip">' +
                        '<i class="material-icons">close</i>' +
                        translation + ' (' + value + ')' +
                    '</div>';
    }

    committeeChipsDiv.innerHTML = chipHTML;
}
