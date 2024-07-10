// Function to create popup content

let popupContent = '<ul>';
let unwanted = ["OID_", "OID", "OBJECTID", "info_src", "cur_miss", "loc_id", "route_id"];
export async function createCarrierPointPopupContent(clickedfeature) {
    // Fetch the alias mapping JSON file
    const response = await fetch('./data/locations_columns.json');
    const columnDictionaries = await response.json();
    const aliasMapping = columnDictionaries['field_aliases'];
    console.log("Alias Mapping: ", Object.keys(aliasMapping));
    for (let property in clickedfeature.properties) {
        // Use alias if available, otherwise use the original property name
        const aliasProperty = aliasMapping[property] || property;
        if (!unwanted.includes(property)) {
            popupContent += `<li><strong>${aliasProperty}</strong>: ${clickedfeature.properties[property]}</li>`
        } else if (property === "cur_miss") {
            let shorterText = clickedfeature.properties[property].substring(0, 42)
            popupContent += `<li><strong>${aliasProperty}</strong>: ${shorterText}</li>`
        }
    }
    return popupContent;
}

export async function createRouteLinePopupContent(clickedfeature) {
    // Fetch the alias mapping JSON file
    const response = await fetch('./data/routes_columns.json');
    const columnDictionaries = await response.json();
    const aliasMapping = columnDictionaries['field_aliases'];
    console.log("Route Alias Mapping: ", Object.keys(aliasMapping));

    // Generate the popup content
    for (let property in clickedfeature.properties) {
        // Use alias if available, otherwise use the original property name
        const aliasProperty = aliasMapping[property] || property;
        if (!unwanted.includes(property)) {
            popupContent += `<li><strong>${aliasProperty}</strong>: ${clickedfeature.properties[property]}</li>`
        } else if (property === "cur_miss") {
            let shorterText = clickedfeature.properties[property].substring(0, 42)
            popupContent += `<li><strong>${aliasProperty}</strong>: ${shorterText}</li>`
        }
    }
    return popupContent;
}