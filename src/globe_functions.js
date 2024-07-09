

// Function to draw route
function drawRoute(map, pastPoint, currentPoint, futurePoint) {
    const route = {
        type: 'Feature',
        geometry: {
            type: 'LineString',
            coordinates: [pastPoint.geometry.coordinates, currentPoint.geometry.coordinates, futurePoint.geometry.coordinates]
        }
    };

    if (map.getSource('route')) {
        map.getSource('route').setData(route);
    } else {
        map.addSource('route', {
            type: 'geojson',
            data: route
        });

        map.addLayer({
            id: 'route',
            type: 'line',
            source: 'route',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': '#888',
                'line-width': 8
            }
        });
    }
}

export { drawRoute };