// Function to create popup content


let unwanted = ["OID_", "OID", "OBJECTID", "info_src", "cur_miss", "loc_id", "route_id"];
export async function createCarrierPointPopupContent(clickedfeature) {
    // Fetch the alias mapping JSON file
    let popupContent = '';
    const response = await fetch('./data/locations_columns.json');
    const columnDictionaries = await response.json();
    const aliasMapping = columnDictionaries['field_aliases'];
    console.log("Alias Mapping: ", Object.keys(aliasMapping));
    for (let property in clickedfeature.properties) {
        // Use alias if available, otherwise use the original property name
        const aliasProperty = aliasMapping[property] || property;

        if (!unwanted.includes(property)) {
            let value = clickedfeature.properties[property];
            if (property.toLowerCase().includes('date') && typeof value === 'string'
            && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/))
                {
                value = value.substring(0, 10); // Extract the date part
            }
            popupContent += `<p><strong>${aliasProperty}</strong>: ${clickedfeature.properties[property]}</p>`

        } else if (property === "cur_miss") {
            let shorterText = clickedfeature.properties[property].substring(0, 42)
            popupContent += `<p><strong>${aliasProperty}</strong>: ${shorterText}</p>`
        }
    }
    return popupContent;
}

export async function createRouteLinePopupContent(clickedfeature) {
    // Fetch the alias mapping JSON file
    let popupContent = '';
    const response = await fetch('./data/routes_columns.json');
    const columnDictionaries = await response.json();
    const aliasMapping = columnDictionaries['field_aliases'];
    console.log("Route Alias Mapping: ", Object.keys(aliasMapping));

    // Generate the popup content
    for (let property in clickedfeature.properties) {
        // Use alias if available, otherwise use the original property name
        const aliasProperty = aliasMapping[property] || property;
        if (!unwanted.includes(property)) {
            let value = clickedfeature.properties[property];
            if (property.toLowerCase().includes('date') && typeof value === 'string'
            && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/))
                {
                value = value.substring(0, 10); // Extract the date part
            }
            popupContent += `<p><strong>${aliasProperty}</strong>: ${value}</p>`

        } else if (property === "cur_miss") {
            let shorterText = clickedfeature.properties[property].substring(0, 42)
            popupContent += `<p><strong>${aliasProperty}</strong>: ${shorterText}</p>`
        }
    }
    return popupContent;
}

// Function to fit map to the bounds of the specified layer
export function fitMapToFeatureBounds(map, feature) {
    // Create a new LngLatBounds object
    const bounds = new mapboxgl.LngLatBounds();

    // Get the coordinates of the feature
    const coordinates = feature.geometry.coordinates;

    // Extend the bounds to include the coordinates of the feature
    coordinates.forEach(coord => {
        bounds.extend(coord);
    });

    // Fit the map to the bounds with a padding of 20, a max zoom of 15, and a duration of 1000
    map.fitBounds(bounds, {
        padding: 20,
        maxZoom: 15,
        duration: 1000
    });
}