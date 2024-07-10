// Function to fit map to the bounds of the specified layer
function fitMapToLayerBounds(layerId) {
    const features = map.queryRenderedFeatures({ layers: [layerId] });
    if (features.length) {
        const bounds = features.reduce((bounds, feature) => {
            return bounds.extend(feature.geometry.coordinates.reduce((innerBounds, coord) => {
                return innerBounds.extend(coord);
            }, new mapboxgl.LngLatBounds(coord, coord)));
        }, new mapboxgl.LngLatBounds(features[0].geometry.coordinates[0], features[0].geometry.coordinates[0]));

        map.fitBounds(bounds, {
            padding: 20,
            maxZoom: 15,
            duration: 1000
        });
    }
}