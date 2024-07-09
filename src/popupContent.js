// Function to create popup content
export function createCarrierPointPopupContent(clickedfeature, alias_mapping)
{
    let popupContent = '<ul>';
    for (let property in clickedfeature.properties)
    {
        // Use alias if available, otherwise use the original property name
        const aliasProperty = alias_mapping[property] || property;
        if (!["info_src", "cur_miss"].includes(property)) {
            popupContent += `<li><strong>${aliasProperty}</strong>: ${clickedfeature.properties[property]}</li>`
        }
        else if (property === "cur_miss") {
            let shorterText = clickedfeature.properties[property].substring(0, 42)
            popupContent += `<li><strong>${aliasProperty}</strong>: ${shorterText}</li>`
        }
    }
    return popupContent;
}